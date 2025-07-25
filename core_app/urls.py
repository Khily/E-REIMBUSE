from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Import semua ViewSet dan juga view fungsi Anda
from .views import (
    RoleViewSet,
    UserProfileViewSet,
    ReimbursementRequestViewSet,
    OwnerUserViewSet,
    admin_page_view,
    login_process_view,
    logout_view,
    manage_user_view,
    add_user_view,
    edit_user_view,
    delete_user_view,
    manage_role_view,
    add_role_view,
    edit_role_view,
    delete_role_view,
    view_request_view,
    user_dashboard_view,
    reimburse_form_view,
    reimburse_success_view,
    history_view,
    panduan_view,
    approve_request_view,
    reject_request_view,
    evidence_view,
    export_requests_excel,
    # HAPUS 'history_detail_view' KARENA TIDAK ADA DI views.py
)

app_name = 'core_app'

router = DefaultRouter()
router.register(r'roles', RoleViewSet)
router.register(r'user-profiles', UserProfileViewSet, basename='userprofile')
router.register(r'reimbursement-requests', ReimbursementRequestViewSet, basename='reimbursement') 
router.register(r'owner-users', OwnerUserViewSet)

urlpatterns = [
    # === URL UNTUK HALAMAN WEB BIASA ===
    path('dashboard/', admin_page_view, name='admin_dashboard'),
    path('user/dashboard/', user_dashboard_view, name='user_dashboard'),
    path('login-process/', login_process_view, name='login_process'),
    path('logout/', logout_view, name='logout'),
    
    # --- URL UNTUK USER MANAGEMENT ---
    path('manage-user/', manage_user_view, name='manage_user'),
    path('manage-user/add/', add_user_view, name='add_user'),
    path('manage-user/edit/<int:pk>/', edit_user_view, name='edit_user'),
    path('manage-user/delete/<int:pk>/', delete_user_view, name='delete_user'),
    
    # --- URL UNTUK ROLE MANAGEMENT ---
    path('manage-role/', manage_role_view, name='manage_role'),
    path('manage-role/add/', add_role_view, name='add_role'),
    path('manage-role/edit/<int:pk>/', edit_role_view, name='edit_role'),
    path('manage-role/delete/<int:pk>/', delete_role_view, name='delete_role'),
    
    # --- URL UNTUK REIMBURSEMENT ---
    path('reimburse/new/', reimburse_form_view, name='reimburse_form'),
    path('reimburse/success/<int:pk>/', reimburse_success_view, name='reimburse_success'),
    
    # --- URL UNTUK AKSI ADMIN ---
    path('request/approve/<int:pk>/', approve_request_view, name='approve_request'),
    path('request/reject/<int:pk>/', reject_request_view, name='reject_request'),

    # --- URL LAINNYA ---
    path('view-request/', view_request_view, name='view_request'),
    path('export-requests-excel/', export_requests_excel, name='export_requests_excel'),
    path('history/', history_view, name='history'),
    path('panduan/', panduan_view, name='panduan'),
    
    # =================================================================================
    # PERBAIKAN: Gunakan SATU URL untuk melihat detail/evidence, yaitu 'evidence_view'.
    # URL ini bisa dipakai oleh admin dan user.
    # =================================================================================
    path('evidence/<int:pk>/', evidence_view, name='reimbursement_detail'),

    # === URL UNTUK API ANDA (otomatis dibuat oleh router) ===
    path('api/', include(router.urls)), # Saya tambahkan 'api/' agar lebih rapi
]