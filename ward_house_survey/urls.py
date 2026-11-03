from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/survey/', include('survey.urls')),
    # Built-in API Testing Dashboard
    path('dashboard/', TemplateView.as_view(template_name='dashboard/index.html'), name='dashboard'),
    path('', TemplateView.as_view(template_name='dashboard/index.html'), name='home'),
]

# Serve media files (house photos) during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
