# backend/core_app/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .forms import CustomUserCreationForm
from .models import CustomUser, Role, UserProfile, ReimbursementRequest

# --- Inline untuk UserProfile ---
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil'
    fields = ('role', 'plat_number')

# --- Custom Admin untuk CustomUser ---
class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    model = CustomUser

    # Form saat mengedit user
    fieldsets = (
        (None, {'fields': ('personal_number', 'password')}),
        ('Informasi Pribadi', {'fields': ('full_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Tanggal Penting', {'fields': ('last_login', 'date_joined')}),
    )

    # Form saat menambahkan user baru
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('personal_number', 'full_name', 'email', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
        ('Permissions', {
            'fields': ('is_superuser', 'groups', 'user_permissions'),
        }),
    )

    list_display = ('personal_number', 'full_name', 'email', 'is_staff', 'is_active')
    search_fields = ('personal_number', 'full_name', 'email')
    ordering = ('personal_number',)
    filter_horizontal = ('groups', 'user_permissions',)
    inlines = (UserProfileInline,)

# Unregister Group jika perlu
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

# Register CustomUser dengan admin yang dikustom
admin.site.register(CustomUser, CustomUserAdmin)

# Register Role
admin.site.register(Role)

# --- Admin untuk ReimbursementRequest ---
@admin.register(ReimbursementRequest)
class ReimbursementRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user_display', 'owner_user_display', 'reimburse_date',
        'total_reimbursement_amount', 'status', 'approved_by_display', 'verified_by_display'
    )
    list_filter = ('status', 'fuel_type', 'reimburse_date', 'submission_date')
    search_fields = (
        'user__personal_number', 'user__full_name', 'owner_user__personal_number',
        'owner_user__full_name', 'notes'
    )
    raw_id_fields = ('user', 'owner_user', 'approved_by', 'verified_by')
    readonly_fields = ('submission_date', 'approved_date', 'verified_date', 'total_reimbursement_amount')

    def user_display(self, obj):
        return obj.user.full_name if obj.user else 'N/A'
    user_display.short_description = 'Pengaju'

    def owner_user_display(self, obj):
        return obj.owner_user.full_name if obj.owner_user else 'N/A'
    owner_user_display.short_description = 'Pemilik Kendaraan'

    def approved_by_display(self, obj):
        return obj.approved_by.full_name if obj.approved_by else 'N/A'
    approved_by_display.short_description = 'Disetujui Oleh'

    def verified_by_display(self, obj):
        return obj.verified_by.full_name if obj.verified_by else 'N/A'
    verified_by_display.short_description = 'Diverifikasi Oleh'
