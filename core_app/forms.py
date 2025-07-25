# di core_app/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Role, CustomUser, ReimbursementRequest

# Form untuk MEMBUAT user baru (dari Anda, sudah sangat bagus)
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('personal_number', 'full_name', 'email')

# Form untuk MENGEDIT data user (tanpa password)
class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('personal_number', 'full_name', 'email')

# Form untuk data UserProfile (role dan plat nomor)
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('role', 'plat_number')

# --- Form Baru untuk Role ---
class RoleForm(forms.ModelForm):
    """
    Form untuk membuat dan mengedit Role.
    """
    class Meta:
        model = Role
        fields = ['name', 'monthly_limit']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Contoh: IT Staff, Marketing'}),
            'monthly_limit': forms.NumberInput(attrs={'placeholder': 'Contoh: 500000'}),
        }

# --- Form Baru untuk Reimbursement ---
class ReimbursementRequestForm(forms.ModelForm):
    class Meta:
        model = ReimbursementRequest
        # Tentukan field yang akan ditampilkan di form
        fields = [
            'reimburse_date',
            'fuel_type',
            'fuel_amount_liter',
            'fuel_price',
            'speedometer_before',
            'speedometer_after',
            'fuel_receipt',
            'owner_user' # Field ini akan kita atur di view
        ]
        widgets = {
            'reimburse_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input-style'}),
            'fuel_type': forms.Select(attrs={'class': 'form-input-style'}),
            'fuel_amount_liter': forms.NumberInput(attrs={'placeholder': 'Contoh: 25.5', 'class': 'form-input-style'}),
            'fuel_price': forms.NumberInput(attrs={'placeholder': 'Contoh: 10000', 'class': 'form-input-style'}),
            'owner_user': forms.Select(attrs={'class': 'form-input-style'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Jika pengguna adalah seorang driver, kita isi pilihan 'owner_user'
        if user and hasattr(user, 'profile') and user.profile.is_driver():
            # Dapatkan semua user yang punya plat nomor (pemilik mobil)
            # Tambahkan filter yang lebih luas untuk menampilkan lebih banyak user
            available_owners = CustomUser.objects.filter(
                profile__plat_number__isnull=False,
                profile__plat_number__gt=''  # Pastikan plat_number tidak kosong
            ).exclude(id=user.id).select_related('profile').order_by('full_name')
            
            self.fields['owner_user'].queryset = available_owners
            # Jika tidak ada owner yang tersedia, tampilkan semua user dengan profile
            if not available_owners.exists():
                all_users = CustomUser.objects.filter(
                    profile__isnull=False
                ).exclude(id=user.id).select_related('profile').order_by('full_name')
                self.fields['owner_user'].queryset = all_users
        else:
            # Jika bukan driver, sembunyikan dan non-aktifkan field ini
            self.fields['owner_user'].widget = forms.HiddenInput()
            self.fields['owner_user'].required = False
