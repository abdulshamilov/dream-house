import django_filters
from .models import Card

class CardFilter(django_filters.FilterSet):
    house_type = django_filters.ChoiceFilter(choices=Card.HOUSE_TYPE_CHOICES)
    city = django_filters.ChoiceFilter(choices=Card.CITY_CHOICES)
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    rooms_min = django_filters.NumberFilter(field_name='rooms', lookup_expr='gte')
    rooms_max = django_filters.NumberFilter(field_name='rooms', lookup_expr='lte')

    class Meta:
        model = Card
        fields = ['house_type', 'city', 'price_min', 'price_max', 'rooms_min', 'rooms_max']
