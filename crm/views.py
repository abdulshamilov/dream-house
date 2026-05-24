from django.db.models import Q, Count
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Lead, Manager, LeadHistory
from .permissions import WebhookPermission, BotAPIPermission
from .serializers import (
    LeadSerializer, LeadCreateSerializer, LeadUpdateSerializer, ManagerSerializer,
)


def _get_manager_from_request(request):
    tg_id = request.headers.get('X-Telegram-Id')
    if not tg_id:
        return None
    try:
        return Manager.objects.get(telegram_id=int(tg_id))
    except (Manager.DoesNotExist, ValueError):
        return None


class LeadViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_permissions(self):
        if self.action == 'create':
            return [WebhookPermission()]
        return [BotAPIPermission()]

    def get_serializer_class(self):
        if self.action == 'create':
            return LeadCreateSerializer
        if self.action == 'partial_update':
            return LeadUpdateSerializer
        return LeadSerializer

    def get_queryset(self):
        qs = Lead.objects.select_related('assigned_to').prefetch_related('history__manager')
        manager = _get_manager_from_request(self.request)
        if manager and not manager.is_admin:
            qs = qs.filter(assigned_to=manager)

        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(phone__icontains=q))

        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        if self.request.query_params.get('overdue'):
            threshold = timezone.now() - timezone.timedelta(days=2)
            qs = qs.filter(status__in=['new', 'assigned', 'in_work'], created_at__lt=threshold)

        return qs

    def perform_create(self, serializer):
        lead = serializer.save()
        LeadHistory.objects.create(lead=lead, action='created')

    def partial_update(self, request, *args, **kwargs):
        lead = self.get_object()
        old_status = lead.status
        old_assigned_id = lead.assigned_to_id

        # Pop comment before passing to serializer
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        comment = data.pop('comment', '') or ''
        if isinstance(comment, list):
            comment = comment[0] if comment else ''

        serializer = LeadUpdateSerializer(lead, data=data, partial=True)
        serializer.is_valid(raise_exception=True)

        manager = _get_manager_from_request(request)

        new_status = serializer.validated_data.get('status', old_status)
        new_assigned = serializer.validated_data.get('assigned_to', lead.assigned_to)

        extra = {}
        if new_assigned and getattr(new_assigned, 'pk', None) != old_assigned_id:
            extra['assigned_at'] = timezone.now()
        if new_status in ('deal', 'rejected') and old_status not in ('deal', 'rejected'):
            extra['closed_at'] = timezone.now()

        lead._skip_bot_notification = True  # ставим ДО save, чтобы сигнал увидел флаг
        lead = serializer.save(**extra)

        # History entries
        if new_assigned and getattr(new_assigned, 'pk', None) != old_assigned_id:
            action_type = 'reassigned' if old_assigned_id else 'assigned'
            LeadHistory.objects.create(lead=lead, manager=manager, action=action_type)

        if new_status != old_status:
            LeadHistory.objects.create(
                lead=lead, manager=manager, action='status_changed',
                from_status=old_status, to_status=new_status,
            )

        if comment:
            LeadHistory.objects.create(
                lead=lead, manager=manager, action='comment', comment=comment,
            )

        return Response(LeadSerializer(lead).data)

    @action(detail=False, methods=['get'], permission_classes=[BotAPIPermission])
    def stats(self, request):
        by_status = {
            item['status']: item['count']
            for item in Lead.objects.values('status').annotate(count=Count('id'))
        }
        managers = []
        for m in Manager.objects.filter(active=True):
            managers.append({
                'name': m.name,
                'telegram_id': m.telegram_id,
                'is_admin': m.is_admin,
                'total': m.leads.count(),
                'active': m.leads.filter(status__in=['assigned', 'in_work', 'meeting']).count(),
                'deals': m.leads.filter(status='deal').count(),
                'rejected': m.leads.filter(status='rejected').count(),
            })
        return Response({
            'total': Lead.objects.count(),
            'by_status': by_status,
            'managers': managers,
        })


class ManagerViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [BotAPIPermission]
    serializer_class = ManagerSerializer
    queryset = Manager.objects.filter(active=True)
