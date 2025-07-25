from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # URL untuk menampilkan halaman login (index.html)
    path('', TemplateView.as_view(template_name="index.html"), name='home'),

    # Baris ini diubah untuk memaksa registrasi namespace 'core_app'
    path('api/', include(('core_app.urls', 'core_app'), namespace='core_app')),
]

# Tambahkan konfigurasi untuk serving media files dalam development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)