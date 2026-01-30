import django_filters
from django.db.models import Q, F, DecimalField, Case, When, Value, ExpressionWrapper
from .models import Card


class CardFilter(django_filters.FilterSet):
    # Поиск по тексту
    search = django_filters.CharFilter(
        method='filter_search',
        label='Поиск по названию, описанию, адресу'
    )
    
    house_type = django_filters.ChoiceFilter(choices=Card.HOUSE_TYPE_CHOICES)
    city = django_filters.ChoiceFilter(choices=Card.CITY_CHOICES)
    building_material = django_filters.ChoiceFilter(choices=Card.BUILDING_MATERIAL_CHOICES)
    category = django_filters.ChoiceFilter(choices=Card.CATEGORY_CHOICES)
    finishing = django_filters.ChoiceFilter(choices=Card._meta.get_field('finishing').choices)
    balcony = django_filters.BooleanFilter(field_name='balcony')
    loggia = django_filters.BooleanFilter(field_name='loggia')
    elevator = django_filters.MultipleChoiceFilter(
        choices=Card.ELEVATOR_CHOICES,
        field_name='elevator',
        conjoined=False,
        label='Тип лифта (можно несколько)'
    )
    parking = django_filters.ChoiceFilter(choices=Card.PARKING_CHOICES)

    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    rooms_min = django_filters.NumberFilter(field_name='rooms', lookup_expr='gte')
    rooms_max = django_filters.NumberFilter(field_name='rooms', lookup_expr='lte')
    area_min = django_filters.NumberFilter(field_name='area', lookup_expr='gte')
    area_max = django_filters.NumberFilter(field_name='area', lookup_expr='lte')
    floors_min = django_filters.NumberFilter(field_name='floors_total', lookup_expr='gte')
    floors_max = django_filters.NumberFilter(field_name='floors_total', lookup_expr='lte')
    
    # Новые фильтры для цены за кв. метр и высоты потолков
    price_per_sqm_min = django_filters.NumberFilter(
        method='filter_price_per_sqm_min',
        label='Минимальная цена за кв. метр'
    )
    price_per_sqm_max = django_filters.NumberFilter(
        method='filter_price_per_sqm_max',
        label='Максимальная цена за кв. метр'
    )
    ceiling_height_min = django_filters.NumberFilter(
        field_name='ceiling_height', 
        lookup_expr='gte',
        label='Минимальная высота потолков'
    )
    ceiling_height_max = django_filters.NumberFilter(
        field_name='ceiling_height', 
        lookup_expr='lte',
        label='Максимальная высота потолков'
    )

    class Meta:
        model = Card
        fields = [
            'search',
            'house_type', 'city', 'building_material', 'category',
            'finishing', 'balcony', 'loggia',
            'elevator', 'parking',
            'price_min', 'price_max',
            'rooms_min', 'rooms_max',
            'area_min', 'area_max',
            'floors_min', 'floors_max',
            'price_per_sqm_min', 'price_per_sqm_max',
            'ceiling_height_min', 'ceiling_height_max'
        ]
    
    def filter_search(self, queryset, name, value):
        """Поиск по названию, описанию и адресу."""
        if value:
            return queryset.filter(
                Q(title__icontains=value) |
                Q(description__icontains=value) |
                Q(address__icontains=value)
            )
        return queryset
    
    def filter_price_per_sqm_min(self, queryset, name, value):
        """Фильтр минимальной цены за кв. метр"""
        if value:
            # Вычисляем цену за кв. метр через ExpressionWrapper
            queryset = queryset.annotate(
                price_per_sqm=Case(
                    When(area__gt=0, then=ExpressionWrapper(
                        F('price') * 1.0 / F('area'),
                        output_field=DecimalField()
                    )),
                    default=Value(0),
                    output_field=DecimalField()
                )
            ).filter(price_per_sqm__gte=value)
        return queryset
    
    def filter_price_per_sqm_max(self, queryset, name, value):
        """Фильтр максимальной цены за кв. метр"""
        if value:
            # Вычисляем цену за кв. метр через ExpressionWrapper
            queryset = queryset.annotate(
                price_per_sqm=Case(
                    When(area__gt=0, then=ExpressionWrapper(
                        F('price') * 1.0 / F('area'),
                        output_field=DecimalField()
                    )),
                    default=Value(0),
                    output_field=DecimalField()
                )
            ).filter(price_per_sqm__lte=value)
        return queryset
