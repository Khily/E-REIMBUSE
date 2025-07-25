# backend/core_app/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import Role, UserProfile, ReimbursementRequest
from django.contrib.auth import get_user_model # Import fungsi get_user_model

User = get_user_model() # Dapatkan CustomUser

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'personal_number'  # override field username

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Tambahkan informasi tambahan ke dalam token jika diperlukan
        token['full_name'] = user.full_name
        token['role'] = user.profile.role.name if hasattr(user, 'profile') else ''
        return token
# Serializer untuk CustomUser Model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'personal_number', 'full_name', 'email']

# Serializer untuk Role Model
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

# Serializer untuk UserProfile Model
class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # Menampilkan detail CustomUser dari user
    role = RoleSerializer(read_only=True) # Menampilkan detail role

    class Meta:
        model = UserProfile
        fields = '__all__'

# Serializer untuk ReimbursementRequest Model
class ReimbursementRequestSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True) # Menampilkan detail UserProfile dari pengaju
    owner_user = UserProfileSerializer(read_only=True) # Menampilkan detail UserProfile dari pemilik kendaraan (jika driver)

    # Tambahkan field untuk URL gambar agar bisa diakses dari frontend
    speedometer_before_url = serializers.SerializerMethodField()
    speedometer_after_url = serializers.SerializerMethodField()
    fuel_receipt_url = serializers.SerializerMethodField()

    class Meta:
        model = ReimbursementRequest
        fields = [
            'id', 'user', 'owner_user', 'submission_date', 'reimburse_date',
            'fuel_type', 'fuel_amount_liter', 'fuel_price', 'total_reimbursement_amount',
            'speedometer_before', 'speedometer_after', 'fuel_receipt',
            'speedometer_before_url', 'speedometer_after_url', 'fuel_receipt_url', # URL gambar
            'status', 'approved_by', 'approved_date', 'verified_by', 'verified_date', 'notes',
            'get_plat_number' # Mengambil property dari model
        ]
        # Pastikan field ini read_only agar tidak bisa diubah langsung via API POST/PUT/PATCH
        read_only_fields = [
            'total_reimbursement_amount', 'submission_date', 'approved_by', 'approved_date',
            'verified_by', 'verified_date', 'get_plat_number'
        ]

    # Metode untuk mendapatkan URL gambar (penting untuk ImageField)
    def get_speedometer_before_url(self, obj):
        if obj.speedometer_before:
            # Gunakan request dari context untuk build absolute URL
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.speedometer_before.url)
            return obj.speedometer_before.url # Fallback jika request tidak ada
        return None

    def get_speedometer_after_url(self, obj):
        if obj.speedometer_after:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.speedometer_after.url)
            return obj.speedometer_after.url
        return None

    def get_fuel_receipt_url(self, obj):
        if obj.fuel_receipt:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.fuel_receipt.url)
            return obj.fuel_receipt.url
        return None
    
    # Overwrite create method untuk menangani field user dan owner_user secara otomatis
    def create(self, validated_data):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            # User yang sedang login adalah pengaju
            validated_data['user'] = request.user
            
            # Logika owner_user untuk driver
            owner_user_id = validated_data.pop('owner_user', None) # Ambil dan hapus dari validated_data
            if request.user.profile.is_driver():
                if owner_user_id:
                    try:
                        owner_user_instance = User.objects.get(id=owner_user_id.id) # owner_user dari serializer sudah jadi instance User
                        validated_data['owner_user'] = owner_user_instance
                    except User.DoesNotExist:
                        raise serializers.ValidationError({"owner_user": "Pemilik kendaraan tidak ditemukan."})
                else:
                    raise serializers.ValidationError({"owner_user": "Driver harus memilih pemilik kendaraan."})
            elif owner_user_id: # Karyawan tidak boleh punya owner_user
                raise serializers.ValidationError({"owner_user": "Karyawan tidak boleh memilih pemilik kendaraan."})

        return super().create(validated_data)

    # Overwrite to_internal_value untuk mengambil owner_user sebagai ID (untuk POST/PUT)
    def to_internal_value(self, data):
        # Proses file uploads terlebih dahulu
        files_data = {}
        for field_name in ['speedometer_before', 'speedometer_after', 'fuel_receipt']:
            if field_name in data and data[field_name]:
                files_data[field_name] = data[field_name]
        
        # Hapus file dari data untuk diproses secara terpisah
        data = {k: v for k, v in data.items() if k not in files_data}

        # Dapatkan ID owner_user jika ada, lalu ubah ke instance User di perform_create
        if 'owner_user' in data and data['owner_user']:
            try:
                owner_id = int(data['owner_user'])
                data['owner_user'] = User.objects.get(id=owner_id) # Jadikan instance User
            except (ValueError, User.DoesNotExist):
                raise serializers.ValidationError({"owner_user": "ID pemilik kendaraan tidak valid."})
        
        # Panggil to_internal_value parent
        internal_value = super().to_internal_value(data)
        internal_value.update(files_data) # Tambahkan kembali file

        return internal_value