"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import sys

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('denuncias.urls')),
]

if settings.DEBUG or 'runserver' in sys.argv:
    # Serve media files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Determine a static files directory to serve in development.
    static_root = None
    if getattr(settings, 'STATIC_ROOT', None):
        static_root = settings.STATIC_ROOT
    elif getattr(settings, 'STATICFILES_DIRS', None):
        # Use the first configured static files dir
        static_root = settings.STATICFILES_DIRS[0]

    if static_root:
        urlpatterns += static(settings.STATIC_URL, document_root=str(static_root))
