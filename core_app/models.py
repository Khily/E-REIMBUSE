from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import MinValueValidator
from django.utils import timezone

# --- CUSTOM USER MANAGER ---
class CustomUserManager(BaseUserManager):
    def create_user(self, personal_number, password=None, **extra_fields):
        if not personal_number:
            raise ValueError('Personal Number harus diatur')
        user = self.model(personal_number=personal_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, personal_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser harus memiliki is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser harus memiliki is_superuser=True.')

        return self.create_user(personal_number, password, **extra_fields)

# --- CUSTOM USER MODEL ---
class CustomUser(AbstractBaseUser, PermissionsMixin):
    personal_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Personal Number"
    )
    full_name = models.CharField(max_length=100, verbose_name="Nama Lengkap")
    email = models.EmailField(unique=True, null=True, blank=True, verbose_name="Email")

    is_staff = models.BooleanField(default=False, verbose_name="Staf")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="Tanggal Bergabung")

    USERNAME_FIELD = 'personal_number'
    REQUIRED_FIELDS = ['full_name']

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Pengguna Aplikasi"
        verbose_name_plural = "Pengguna Aplikasi"
        ordering = ['personal_number']

    def __str__(self):
        # Diperbaiki: Memberikan fallback jika nama lengkap kosong
        return self.full_name or self.personal_number

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name

# --- ROLE MODEL ---
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Nama Role")
    monthly_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True, blank=True,
        verbose_name="Batas Reimbursement Bulanan (Rp)"
    )

    class Meta:
        verbose_name = "Role Pegawai"
        verbose_name_plural = "Role Pegawai"
        ordering = ['name']

    def __str__(self):
        # Diperbaiki: Menangani kasus jika limit adalah None
        if self.monthly_limit is not None:
            # Menggunakan format lokal Indonesia untuk angka
            limit_str = f"Rp {self.monthly_limit:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return f"{self.name} (Limit: {limit_str})"
        return self.name or "Role Tanpa Nama"

# --- USERPROFILE MODEL ---
class UserProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Akun Pengguna"
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='users',
        verbose_name="Role Pegawai"
    )
    plat_number = models.CharField(
        max_length=20,
        null=True, blank=True,
        verbose_name="Nomor Plat Kendaraan"
    )

    class Meta:
        verbose_name = "Detail Profil Pengguna"
        verbose_name_plural = "Detail Profil Pengguna"
        ordering = ['user__personal_number']

    def __str__(self):
        # Menggunakan __str__ dari model User yang sudah diperbaiki
        return self.user.__str__()

    def is_driver(self):
        return self.role and self.role.name.lower() == 'driver'

    def is_admin_role(self):
        return self.role and self.role.name.lower() == 'admin'

    def is_supervisor_role(self):
        return self.role and self.role.name.lower() == 'supervisor'

    def is_employee_role(self):
        return self.role and self.role.name.lower() == 'karyawan'

# --- REIMBURSEMENTREQUEST MODEL ---
class ReimbursementRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Menunggu Persetujuan'),
        ('Approved', 'Disetujui'),
        ('Rejected', 'Ditolak'),
        ('Returned', 'Dikembalikan untuk Revisi'),
        ('Verified', 'Terverifikasi (Siap Cair)'),
        ('Paid', 'Sudah Cair'),
    ]

    FUEL_TYPE_CHOICES = [
        ('Pertalite', 'Pertalite'),
        ('Pertamax', 'Pertamax'),
        ('Solar', 'Solar'),
        ('Lainnya', 'Lainnya'),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reimbursement_requests',
        verbose_name="Pengaju Reimbursement"
    )
    owner_user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='driver_reimbursements',
        verbose_name="Pemilik Kendaraan (Jika Driver)"
    )
    submission_date = models.DateTimeField(auto_now_add=True, verbose_name="Tanggal Pengajuan")
    reimburse_date = models.DateField(verbose_name="Tanggal Pengisian BBM")
    fuel_type = models.CharField(max_length=50, choices=FUEL_TYPE_CHOICES, verbose_name="Jenis BBM")
    fuel_amount_liter = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Jumlah Liter BBM"
    )
    fuel_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Harga BBM per Liter"
    )
    total_reimbursement_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Total Biaya Reimbursement (Rp)"
    )
    speedometer_before = models.ImageField(upload_to='reimbursement_proofs/', verbose_name="Speedometer Sebelum")
    speedometer_after = models.ImageField(upload_to='reimbursement_proofs/', verbose_name="Speedometer Sesudah")
    fuel_receipt = models.ImageField(upload_to='reimbursement_proofs/', verbose_name="Struk BBM")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        verbose_name="Status Pengajuan"
    )
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approved_requests',
        verbose_name="Disetujui Oleh"
    )
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name="Tanggal Disetujui")
    verified_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='verified_requests',
        verbose_name="Diverifikasi Oleh"
    )
    verified_date = models.DateTimeField(null=True, blank=True, verbose_name="Tanggal Diverifikasi")
    notes = models.TextField(null=True, blank=True, verbose_name="Catatan")

    @property
    def get_plat_number(self):
        if hasattr(self.user, 'profile') and self.user.profile.plat_number:
            return self.user.profile.plat_number
        elif self.owner_user and hasattr(self.owner_user, 'profile') and self.owner_user.profile.plat_number:
            return self.owner_user.profile.plat_number
        return "N/A"

    class Meta:
        verbose_name = "Pengajuan Reimbursement"
        verbose_name_plural = "Pengajuan Reimbursement"
        ordering = ['-submission_date']

    def save(self, *args, **kwargs):
        if self.fuel_amount_liter is not None and self.fuel_price is not None:
            self.total_reimbursement_amount = self.fuel_amount_liter * self.fuel_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pengajuan oleh {self.user} pada {self.submission_date.strftime('%d-%m-%Y')}"
