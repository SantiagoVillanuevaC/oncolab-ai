# ══════════════════════════════════════════════════════
#  ARCHIVO: core/urls.py
#  Proyecto: OncoLab AI — Diagnóstico Médico Asistido
#  Descripción: Configuración de URLs para la app 'core'
# ══════════════════════════════════════════════════════

from django.urls import path
from . import views

urlpatterns = [
    # ── Dashboard principal ──────────────────────────────
    path('', views.dashboard, name='dashboard'),

    # ── Formulario: Nuevo Diagnóstico ────────────────────
    path('diagnostico/nuevo/', views.nuevo_diagnostico, name='nuevo_diagnostico'),

    # ── Resultado del análisis (tras enviar el formulario)
    path('diagnostico/resultado/', views.resultado_diagnostico, name='resultado_diagnostico'),

    # ── Historial completo de pacientes ─────────────────
    path('historial/', views.historial, name='historial'),

    # ── Ver resultado de un diagnóstico por ID ───────────
    path('diagnostico/<int:id>/ver/', views.ver_resultado, name='resultado'),
]


# ══════════════════════════════════════════════════════
#  ARCHIVO: oncolab_project/urls.py   (urls.py RAÍZ)
#  Descripción: Incluye las URLs de la app 'core'
# ══════════════════════════════════════════════════════
#
#  from django.contrib import admin
#  from django.urls import path, include
#
#  urlpatterns = [
#      path('admin/', admin.site.urls),
#      path('', include('core.urls')),   # <-- Agrega esta línea
#  ]
