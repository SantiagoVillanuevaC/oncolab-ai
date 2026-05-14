"""
URL Configuration — OncoLab AI
Archivo raíz de rutas del proyecto Django.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # Todas las rutas de la app core
]
