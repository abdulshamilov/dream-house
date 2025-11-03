import django_filters
from .models import Card


class CardFilter(django_filters.FilterSet):
    house_type = django_filters.ChoiceFilter(choices=Card.HOUSE_TYPE_CHOICES)
    city = django_filters.ChoiceFilter(choices=Card.CITY_CHOICES)  # теперь это идентификаторы
    building_material = django_filters.ChoiceFilter(choices=Card.BUILDING_MATERIAL_CHOICES)
    category = django_filters.ChoiceFilter(choices=Card.CATEGORY_CHOICES)
    elevator = django_filters.ChoiceFilter(choices=Card.ELEVATOR_CHOICES)
    parking = django_filters.ChoiceFilter(choices=Card.PARKING_CHOICES)

    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    rooms_min = django_filters.NumberFilter(field_name='rooms', lookup_expr='gte')
    rooms_max = django_filters.NumberFilter(field_name='rooms', lookup_expr='lte')
    area_min = django_filters.NumberFilter(field_name='area', lookup_expr='gte')
    area_max = django_filters.NumberFilter(field_name='area', lookup_expr='lte')
    floors_min = django_filters.NumberFilter(field_name='floors_total', lookup_expr='gte')
    floors_max = django_filters.NumberFilter(field_name='floors_total', lookup_expr='lte')

    class Meta:
        model = Card
        fields = [
            'house_type', 'city', 'building_material', 'category',
            'elevator', 'parking', 'balcony',
            'price_min', 'price_max',
            'rooms_min', 'rooms_max',
            'area_min', 'area_max',
            'floors_min', 'floors_max'
        ]
