from rest_framework import serializers
from .models import Lead, Manager, LeadHistory


class ManagerSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='name', read_only=True)

    class Meta:
        model = Manager
        fields = ['id', 'full_name', 'name', 'telegram_id', 'telegram_username', 'is_admin', 'active']


class LeadHistorySerializer(serializers.ModelSerializer):
    manager_name = serializers.SerializerMethodField()
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = LeadHistory
        fields = ['id', 'action', 'action_display', 'from_status', 'to_status',
                  'comment', 'manager_name', 'created_at']

    def get_manager_name(self, obj):
        return obj.manager.name if obj.manager else None


class LeadSerializer(serializers.ModelSerializer):
    assigned_to_detail = ManagerSerializer(source='assigned_to', read_only=True)
    history = LeadHistorySerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Lead
        fields = [
            'id', 'name', 'phone', 'jk', 'status', 'status_display',
            'assigned_to', 'assigned_to_detail',
            'source', 'raw_data',
            'created_at', 'assigned_at', 'closed_at',
            'history',
        ]
        read_only_fields = ['created_at', 'assigned_at', 'closed_at']


class LeadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['name', 'phone', 'jk', 'source', 'raw_data']

    def validate_phone(self, value):
        return value.strip()


class LeadUpdateSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(write_only=True, required=False, allow_blank=True, default='')

    class Meta:
        model = Lead
        fields = ['status', 'assigned_to', 'comment']
        extra_kwargs = {
            'status': {'required': False},
            'assigned_to': {'required': False},
        }
