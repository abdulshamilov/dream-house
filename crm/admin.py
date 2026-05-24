from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from django.utils import timezone
from .models import Lead, Manager, LeadHistory

# --- Pin CRM at top of admin index ---
_original_get_app_list = admin.AdminSite.get_app_list

def _get_app_list(self, request, app_label=None):
    app_list = _original_get_app_list(self, request, app_label)
    crm = [a for a in app_list if a['app_label'] == 'crm']
    rest = [a for a in app_list if a['app_label'] != 'crm']
    return crm + rest

admin.AdminSite.get_app_list = _get_app_list

# ---

STATUS_COLORS = {
    'new':      ('#e74c3c', '🔴 Новая'),
    'assigned': ('#e67e22', '🟠 Назначена'),
    'in_work':  ('#f39c12', '🟡 В работе'),
    'meeting':  ('#3498db', '🔵 Встреча'),
    'deal':     ('#27ae60', '🟢 Сделка'),
    'rejected': ('#95a5a6', '⚫ Отказ'),
}


class LeadHistoryInline(admin.TabularInline):
    model = LeadHistory
    extra = 0
    readonly_fields = ['action_badge', 'from_to', 'comment', 'manager', 'created_at']
    fields = ['action_badge', 'from_to', 'comment', 'manager', 'created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def action_badge(self, obj):
        labels = {
            'created': ('🆕', '#3498db'),
            'assigned': ('👤', '#e67e22'),
            'reassigned': ('🔀', '#9b59b6'),
            'status_changed': ('🔄', '#f39c12'),
            'comment': ('💬', '#1abc9c'),
        }
        icon, color = labels.get(obj.action, ('•', '#999'))
        return format_html(
            '<span style="color:{};font-weight:600;">{} {}</span>',
            color, icon, obj.get_action_display(),
        )
    action_badge.short_description = 'Действие'

    def from_to(self, obj):
        if obj.from_status and obj.to_status:
            fc, _ = STATUS_COLORS.get(obj.from_status, ('#999', obj.from_status))
            tc, _ = STATUS_COLORS.get(obj.to_status, ('#999', obj.to_status))
            return format_html(
                '<span style="color:{};">●</span> → <span style="color:{};">●</span> {}→{}',
                fc, tc, obj.from_status, obj.to_status,
            )
        return '—'
    from_to.short_description = 'Переход'


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone', 'jk', 'status_badge', 'assigned_to', 'source_badge', 'created_at']
    list_display_links = ['id', 'name']
    list_filter = ['status', 'source', 'assigned_to', 'created_at']
    search_fields = ['name', 'phone', 'jk']
    readonly_fields = ['created_at', 'assigned_at', 'closed_at', 'raw_data']
    date_hierarchy = 'created_at'
    list_per_page = 25
    inlines = [LeadHistoryInline]
    list_select_related = ['assigned_to']

    fieldsets = (
        ('Клиент', {
            'fields': ('name', 'phone', 'jk'),
        }),
        ('Статус', {
            'fields': ('status', 'assigned_to'),
        }),
        ('Даты', {
            'fields': ('created_at', 'assigned_at', 'closed_at'),
            'classes': ('collapse',),
        }),
        ('Доп. данные', {
            'fields': ('source', 'raw_data'),
            'classes': ('collapse',),
        }),
    )

    def status_badge(self, obj):
        color, label = STATUS_COLORS.get(obj.status, ('#999', obj.status))
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;'
            'border-radius:12px;font-size:11px;font-weight:700;white-space:nowrap;">{}</span>',
            color, label,
        )
    status_badge.short_description = 'Статус'
    status_badge.admin_order_field = 'status'

    def source_badge(self, obj):
        icons = {'site_form': '🌐 Сайт', 'call_request': '📱 Приложение'}
        return icons.get(obj.source, obj.source)
    source_badge.short_description = 'Источник'


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ['name', 'telegram_username', 'is_admin', 'active', 'leads_stats']
    list_filter = ['is_admin', 'active']
    search_fields = ['name', 'telegram_username']
    list_editable = ['is_admin', 'active']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            total=Count('leads'),
            active_count=Count('leads', filter=Q(leads__status__in=['assigned', 'in_work', 'meeting'])),
            deals=Count('leads', filter=Q(leads__status='deal')),
        )

    def leads_stats(self, obj):
        return format_html(
            '<span title="Всего">📋 {}</span> &nbsp;'
            '<span title="Активных" style="color:#f39c12;">⚡ {}</span> &nbsp;'
            '<span title="Сделок" style="color:#27ae60;">✅ {}</span>',
            obj.total, obj.active_count, obj.deals,
        )
    leads_stats.short_description = 'Заявки'


@admin.register(LeadHistory)
class LeadHistoryAdmin(admin.ModelAdmin):
    list_display = ['lead', 'action', 'from_status', 'to_status', 'manager', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['lead__name', 'lead__phone', 'comment']
    readonly_fields = ['lead', 'manager', 'action', 'from_status', 'to_status', 'comment', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
