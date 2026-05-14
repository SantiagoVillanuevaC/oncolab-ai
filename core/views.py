# ══════════════════════════════════════════════════════════════════════
#  ARCHIVO: core/views.py  —  OncoLab AI  (versión corregida final)
# ══════════════════════════════════════════════════════════════════════

import os
import logging
import numpy as np
import joblib

from django.shortcuts import render, redirect
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

# ── Cargar modelos al iniciar Django ──────────────────────────────────
_SCALER_PATH = os.path.join(settings.BASE_DIR, "scaler.pkl")
_MODEL_PATH  = os.path.join(settings.BASE_DIR, "model_kmeans.pkl")

try:
    SCALER = joblib.load(_SCALER_PATH)
    MODELO = joblib.load(_MODEL_PATH)
    MODELOS_CARGADOS = True
    print("✅ Modelos cargados correctamente.")
except FileNotFoundError as e:
    SCALER = None
    MODELO = None
    MODELOS_CARGADOS = False
    print(f"❌ Modelos NO encontrados: {e}")


# ── Vista: Dashboard ──────────────────────────────────────────────────
def dashboard(request):
    historial  = request.session.get('historial_diagnosticos', [])
    ultimos    = list(reversed(historial))[:5]
    context = {
        'ultimos_diagnosticos': ultimos,
        'total_diagnosticos':   len(historial),
        'modelo_activo':        MODELOS_CARGADOS,
    }
    return render(request, 'core/index.html', context)


# ── Vista: Formulario + Predicción ───────────────────────────────────
def nuevo_diagnostico(request):

    if not MODELOS_CARGADOS:
        return render(request, 'core/diagnostico_form.html', {
            'form': {},
            'error': 'El modelo no está cargado. Ejecuta train_and_export.py primero.'
        })

    if request.method == 'POST':
        try:
            pw   = float(request.POST.get("perimeter_worst", 0))
            aw   = float(request.POST.get("area_worst", 0))
            rw   = float(request.POST.get("radius_worst", 0))
            cpm  = float(request.POST.get("concave_points_mean", 0))
            cpw  = float(request.POST.get("concave_points_worst", 0))
            cm   = float(request.POST.get("concavity_mean", 0))
            pm   = float(request.POST.get("perimeter_mean", 0))
            am   = float(request.POST.get("area_mean", 0))

            print("─" * 50)
            print(f"  perimeter_worst:      {pw}")
            print(f"  area_worst:           {aw}")
            print(f"  radius_worst:         {rw}")
            print(f"  concave_points_mean:  {cpm}")
            print(f"  concave_points_worst: {cpw}")
            print(f"  concavity_mean:       {cm}")
            print(f"  perimeter_mean:       {pm}")
            print(f"  area_mean:            {am}")

            X        = np.array([[pw, aw, rw, cpm, cpw, cm, pm, am]])
            X_scaled = SCALER.transform(X)
            cluster  = int(MODELO.predict(X_scaled)[0])

            # Cluster 0 = Maligno / Cluster 1 = Benigno (verificado con pruebas)
            resultado = "Maligno" if cluster == 0 else "Benigno"

            print(f"  Cluster predicho: {cluster}")
            print(f"  Resultado:        {resultado}")
            print("─" * 50)

            id_paciente  = request.POST.get('id_paciente', 'SIN-ID').strip() or 'SIN-ID'
            fecha_actual = timezone.now().strftime('%d/%m/%Y %H:%M')

            request.session['resultado_diagnostico'] = {
                'resultado':   resultado,
                'cluster':     cluster,
                'id_paciente': id_paciente,
                'fecha':       fecha_actual,
                'datos': {
                    'perimeter_worst':      str(pw),
                    'area_worst':           str(aw),
                    'radius_worst':         str(rw),
                    'concave_points_mean':  str(cpm),
                    'concave_points_worst': str(cpw),
                    'concavity_mean':       str(cm),
                    'perimeter_mean':       str(pm),
                    'area_mean':            str(am),
                }
            }

            historial = request.session.get('historial_diagnosticos', [])
            historial.append({
                'id':          len(historial) + 1,
                'id_paciente': id_paciente,
                'fecha':       fecha_actual,
                'resultado':   resultado,
            })
            request.session['historial_diagnosticos'] = historial
            request.session.modified = True

            return redirect('resultado_diagnostico')

        except Exception as e:
            print(f"❌ Error en predicción: {e}")
            return render(request, 'core/diagnostico_form.html', {
                'form':  request.POST,
                'error': f'Error al procesar los datos: {str(e)}'
            })

    return render(request, 'core/diagnostico_form.html', {'form': {}})


# ── Vista: Resultado ──────────────────────────────────────────────────
def resultado_diagnostico(request):
    datos = request.session.get('resultado_diagnostico', None)
    if not datos:
        return redirect('nuevo_diagnostico')

    context = {
        'resultado':   datos.get('resultado', 'Desconocido'),
        'cluster':     datos.get('cluster', '?'),
        'id_paciente': datos.get('id_paciente', 'N/A'),
        'fecha':       datos.get('fecha', '--'),
        'datos':       datos.get('datos', {}),
    }

    del request.session['resultado_diagnostico']
    request.session.modified = True

    return render(request, 'core/resultado.html', context)


# ── Vista: Historial ──────────────────────────────────────────────────
def historial(request):
    todos = list(reversed(request.session.get('historial_diagnosticos', [])))
    return render(request, 'core/historial.html', {
        'diagnosticos': todos,
        'total':        len(todos),
    })


# ── Vista: Ver resultado por ID ───────────────────────────────────────
def ver_resultado(request, id):
    historial_sesion = request.session.get('historial_diagnosticos', [])
    diag = next((d for d in historial_sesion if d.get('id') == id), None)

    context = {
        'resultado':   diag.get('resultado', 'No disponible') if diag else 'No disponible',
        'cluster':     '0' if (diag and diag.get('resultado') == 'Maligno') else '1',
        'id_paciente': diag.get('id_paciente', 'N/A') if diag else f'#{id}',
        'fecha':       diag.get('fecha', '--') if diag else '--',
        'datos':       {f: '—' for f in [
            'perimeter_worst', 'area_worst', 'radius_worst',
            'concave_points_mean', 'concave_points_worst',
            'concavity_mean', 'perimeter_mean', 'area_mean'
        ]},
    }
    return render(request, 'core/resultado.html', context)
