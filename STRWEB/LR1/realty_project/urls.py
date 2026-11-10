"""Корневые URL проекта."""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve as django_static_serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# В учебной работе картинки хранятся в ImageField и должны открываться на Render.
# Поэтому media раздаётся отдельным URL даже при DEBUG=False, если включён
# DJANGO_SERVE_MEDIA_FILES=True. Для реального production лучше Cloudinary/S3.
if settings.DEBUG or getattr(settings, 'SERVE_MEDIA_FILES', False):
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', django_static_serve, {'document_root': settings.MEDIA_ROOT}),
    ]
