from decimal import Decimal

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from .models import Card, InstallmentPlan, CardPromotion
from .serializers import (
    PaymentOptionsSerializer,
    InstallmentCalculateSerializer,
    InstallmentCalculateResultSerializer,
    InstallmentMatchInputSerializer,
    InstallmentMatchResultSerializer,
)


def _active_plans(card):
    today = timezone.now().date()
    return InstallmentPlan.objects.filter(card=card, is_active=True).filter(
        Q(valid_from__isnull=True) | Q(valid_from__lte=today)
    ).filter(
        Q(valid_until__isnull=True) | Q(valid_until__gte=today)
    )


def _active_promotions(card):
    today = timezone.now().date()
    return CardPromotion.objects.filter(card=card, is_active=True).filter(
        Q(valid_from__isnull=True) | Q(valid_from__lte=today)
    ).filter(
        Q(valid_until__isnull=True) | Q(valid_until__gte=today)
    )


class CardPaymentOptionsView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        responses={
            200: PaymentOptionsSerializer,
        },
        description=(
            'Варианты оплаты для карточки. '
            'Если prices_on_request=true — возвращает только флаг и промо. '
            'Иначе: cash_option (объект или null) + installment_options (массив) '
            'с уже посчитанными total_price, down_payment, monthly_payment.'
        ),
    )
    def get(self, request, pk):
        card = get_object_or_404(Card, pk=pk, is_hidden=False)
        promotions = list(_active_promotions(card))

        ctx = {'card': card, 'request': request}

        if card.prices_on_request:
            data = PaymentOptionsSerializer({
                'card_id': card.pk,
                'prices_on_request': True,
                'accepts_car_barter': card.accepts_car_barter,
                'accepts_land_barter': card.accepts_land_barter,
                'cash_option': None,
                'installment_options': [],
                'promotions': promotions,
            }, context=ctx).data
            return Response(data)

        plans = _active_plans(card)
        cash_plan = plans.filter(is_cash=True).first()
        installment_plans = list(plans.filter(is_cash=False).order_by('term_months'))

        data = PaymentOptionsSerializer({
            'card_id': card.pk,
            'prices_on_request': False,
            'accepts_car_barter': card.accepts_car_barter,
            'accepts_land_barter': card.accepts_land_barter,
            'cash_option': cash_plan,
            'installment_options': installment_plans,
            'promotions': promotions,
        }, context=ctx).data
        return Response(data)


class InstallmentCalculateView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=InstallmentCalculateSerializer,
        responses=InstallmentCalculateResultSerializer,
        description='Рассчитать суммы по тарифу рассрочки (total, down_payment, monthly).',
    )
    def post(self, request):
        serializer = InstallmentCalculateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plan = get_object_or_404(
            InstallmentPlan.objects.select_related('card'),
            pk=serializer.validated_data['plan_id'],
            is_active=True,
        )
        card = plan.card
        total_price = plan.total_price_for_card(card)
        down_payment = plan.calculate_down_payment(total_price).quantize(Decimal('0.01'))
        monthly = plan.calculate_monthly_payment(total_price)
        if monthly is not None:
            monthly = monthly.quantize(Decimal('0.01'))

        return Response(InstallmentCalculateResultSerializer({
            'total_price': total_price,
            'down_payment': down_payment,
            'monthly_payment': monthly,
            'term_months': plan.term_months,
        }).data)


class InstallmentMatchView(APIView):
    """
    Калькулятор рассрочки: по сумме взноса и сроку находит подходящий план
    и возвращает ежемесячный платёж.

    Логика матчинга:
    - Планы хранят down_payment_min_amount как нижнюю границу диапазона.
    - Из всех планов, где min_amount <= down_payment, берётся с наибольшим порогом.
    - Например: планы 300к, 500к, 1М; взнос 800к → план 500к.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=InstallmentMatchInputSerializer,
        responses={
            200: InstallmentMatchResultSerializer,
            400: {'description': 'Взнос меньше минимального или срок превышает максимальный'},
        },
        description=(
            'Калькулятор рассрочки. '
            'Принимает down_payment (сумма взноса) и term_months (срок). '
            'Возвращает подходящий план, total_price, down_payment, monthly_payment.'
        ),
    )
    def post(self, request, pk):
        card = get_object_or_404(Card, pk=pk)

        inp = InstallmentMatchInputSerializer(data=request.data)
        inp.is_valid(raise_exception=True)
        down_payment = inp.validated_data['down_payment']
        term_months = inp.validated_data['term_months']

        # Ищем план где down_payment попадает в диапазон [min, max]
        # Если max не задан — нет верхней границы
        plan = (
            _active_plans(card)
            .filter(is_cash=False, down_payment_type='fixed')
            .filter(down_payment_min_amount__lte=down_payment)
            .filter(
                Q(down_payment_max_amount__isnull=True) |
                Q(down_payment_max_amount__gte=down_payment)
            )
            .order_by('-down_payment_min_amount')
            .first()
        )

        if plan is None:
            min_plan = (
                _active_plans(card)
                .filter(is_cash=False, down_payment_type='fixed')
                .order_by('down_payment_min_amount')
                .first()
            )
            min_required = min_plan.down_payment_min_amount if min_plan else None
            return Response(
                {'detail': f'Минимальный взнос: {min_required} ₽'},
                status=400,
            )

        if term_months > plan.term_months:
            return Response(
                {'detail': f'Максимальный срок для этого плана: {plan.term_months} мес.'},
                status=400,
            )

        total_price = plan.total_price_for_card(card)
        monthly = ((total_price - down_payment) / term_months).quantize(Decimal('0.01'))

        down_from = plan.down_payment_min_amount if plan.down_payment_min_amount is not None else Decimal('0')
        down_to = plan.down_payment_max_amount if plan.down_payment_max_amount is not None else total_price

        return Response(InstallmentMatchResultSerializer({
            'plan_id': plan.pk,
            'price_per_sqm': plan.price_per_sqm,
            'total_price': total_price,
            'down_payment': down_payment,
            'down_payment_from': down_from,
            'down_payment_to': down_to,
            'monthly_payment': monthly,
            'term_months': term_months,
            'max_term_months': plan.term_months,
        }).data)
