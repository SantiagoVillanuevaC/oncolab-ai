══════════════════════════════════════════════════════════════════
  OncoLab AI — Diagnóstico Mamario Asistido por Inteligencia Artificial
  Proyecto Final Universitario
══════════════════════════════════════════════════════════════════

ESTRUCTURA DEL PROYECTO
─────────────────────────────────────────────────────────────────
oncolab_project/
│
├── manage.py                    ← Comando principal de Django
├── requirements.txt             ← Dependencias Python
├── train_and_export.py          ← Script para entrenar el modelo
├── Cancer_Data.csv              ← ⚠ DEBES COLOCAR ESTE ARCHIVO AQUÍ
├── scaler.pkl                   ← Se genera al correr train_and_export.py
├── model_kmeans.pkl             ← Se genera al correr train_and_export.py
│
├── oncolab_project/             ← Configuración Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
└── core/                        ← App principal
    ├── views.py                 ← Lógica de vistas + predicción IA
    ├── urls.py                  ← Rutas de la app
    ├── models.py
    ├── apps.py
    ├── migrations/
    └── templates/core/          ← Plantillas HTML
        ├── base.html
        ├── index.html           → Dashboard
        ├── diagnostico_form.html → Formulario de diagnóstico
        ├── resultado.html       → Pantalla de resultados
        └── historial.html       → Historial de pacientes


PASOS PARA EJECUTAR EL PROYECTO
─────────────────────────────────────────────────────────────────

PASO 1 — Instalar dependencias
  Abre una terminal en la carpeta oncolab_project/ y ejecuta:

  pip install -r requirements.txt

PASO 2 — Colocar el dataset
  Copia tu archivo Cancer_Data.csv dentro de oncolab_project/
  (la misma carpeta donde está manage.py y train_and_export.py)

PASO 3 — Entrenar y exportar el modelo
  En la terminal, dentro de oncolab_project/, ejecuta:

  python train_and_export.py

  Esto generará automáticamente:
    ✅ scaler.pkl
    ✅ model_kmeans.pkl

PASO 4 — Aplicar migraciones de Django
  python manage.py migrate

PASO 5 — Iniciar el servidor
  python manage.py runserver

PASO 6 — Abrir en el navegador
  http://127.0.0.1:8000


URLS DEL SISTEMA
─────────────────────────────────────────────────────────────────
  /                          → Dashboard principal
  /diagnostico/nuevo/        → Formulario de diagnóstico
  /diagnostico/resultado/    → Resultado del análisis
  /historial/                → Historial de pacientes
  /admin/                    → Panel de administración Django


TECNOLOGÍAS USADAS
─────────────────────────────────────────────────────────────────
  • Django 5.0          — Framework web Backend
  • Bootstrap 5         — Framework CSS Frontend (vía CDN)
  • FontAwesome 6       — Iconos médicos (vía CDN)
  • scikit-learn        — K-Means Clustering + MinMaxScaler
  • Wisconsin Dataset   — Breast Cancer Wisconsin (Diagnostic)
  • Python 3.10+        — Lenguaje de programación


MÉTRICAS DEL MODELO
─────────────────────────────────────────────────────────────────
  • Algoritmo:        K-Means (k=2, init='k-means++')
  • Silhouette Score: ~0.50
  • Gap Statistic:     0.67
  • Features usadas:  8 (seleccionadas por Random Forest)


NOTAS IMPORTANTES
─────────────────────────────────────────────────────────────────
  ⚠ Este sistema es exclusivamente académico.
  ⚠ No reemplaza el diagnóstico médico profesional.
  ⚠ Si el mapeo Cluster 0/1 se invierte al entrenar,
    el script train_and_export.py lo indicará en consola
    y deberás ajustar una línea en core/views.py
    (está marcada con comentario en el código).

══════════════════════════════════════════════════════════════════
