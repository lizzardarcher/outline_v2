from django.contrib import admin
from django.contrib.auth.models import Group

from apps.bot.models import TelegramBot, TelegramUser, TelegramReferral, ReferralSettings, GlobalSettings, VpnKey, \
    Server, IncomeInfo, Transaction, Price, WithdrawalRequest
from django.conf import settings

DEBUG = settings.DEBUG
# admin.site.site_url = ''
admin.site.site_header = "Outline VPN Админ Панель"
admin.site.site_title = "Outline VPN"
admin.site.index_title = "Добро пожаловать в Outline VPN Админ Панель"
admin.site.unregister(Group)


class WithdrawalRequestInline(admin.TabularInline):
    model = WithdrawalRequest

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class TransactionInline(admin.TabularInline):
    model = Transaction

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class VpnKeyInline(admin.TabularInline):
    model = VpnKey

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = (
        'join_date', 'first_name', 'last_name', 'username', 'subscription_status', 'subscription_expiration')
    search_fields = ('first_name', 'last_name', 'username', 'user_id')
    if not DEBUG:
        readonly_fields = ('join_date', 'first_name', 'last_name', 'username',)
    ordering = ('-subscription_status', 'subscription_expiration',)
    empty_value_display = '---'
    inlines = [TransactionInline, VpnKeyInline, WithdrawalRequestInline]

    def has_add_permission(self, request):
        if not DEBUG:
            return False
        else:
            return True

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(TelegramBot)
class TelegramBotAdmin(admin.ModelAdmin):
    list_display = ('title', 'token', 'username', 'created_at')

    def has_add_permission(self, request):
        if TelegramBot.objects.all():
            return False
        else:
            return True

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(TelegramReferral)
class TelegramReferralAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referred', 'level')

    def has_add_permission(self, request):
        if not DEBUG:
            return False
        else:
            return True

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'currency', 'timestamp')

    def has_add_permission(self, request):
        if not DEBUG:
            return False
        else:
            return True

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'currency', 'timestamp')
    list_editable = ['status']

    def has_add_permission(self, request, obj=None):
        if not DEBUG:
            return False
        else:
            return True

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ReferralSettings)
class ReferralSettingAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        if not DEBUG:
            return False
        else:
            return True

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(GlobalSettings)
class GlobalSettingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if not DEBUG:
            return False
        else:
            return True

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(IncomeInfo)
class IncomeInfo(admin.ModelAdmin):
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(VpnKey)
class VpnKey(admin.ModelAdmin):
    list_display = ('user', 'server', 'is_limit', 'data_limit', 'created_at')

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = (
        'hosting', 'ip_address', 'user', 'password', 'rental_price', 'max_keys', 'keys_generated', 'is_active',
        'created_at')


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if Price.objects.all():
            return False
        else:
            return True

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
