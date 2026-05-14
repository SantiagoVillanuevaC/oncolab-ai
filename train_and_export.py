# ══════════════════════════════════════════════════════════════════════
#  ARCHIVO: train_and_export.py
#  Proyecto: OncoLab AI — Diagnóstico Médico Asistido por IA
#  Descripción: Entrena el MinMaxScaler + K-Means (k=2) con el dataset
#               Wisconsin (Cancer_Data.csv) y exporta ambos modelos
#               como archivos .pkl listos para Django.
#
#  USO:
#    1. Coloca Cancer_Data.csv en la misma carpeta que este script.
#    2. Ejecuta:  python train_and_export.py
#    3. Se generarán: scaler.pkl  y  model_kmeans.pkl
#    4. Copia ambos .pkl a la carpeta raíz de tu proyecto Django.
# ══════════════════════════════════════════════════════════════════════

import os
import numpy as np
import pandas as pd
import joblib

from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


# ──────────────────────────────────────────────────────────────────────
#  CONFIGURACIÓN
# ──────────────────────────────────────────────────────────────────────

# Directorio donde está este mismo archivo .py
_BASE = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH  = os.path.join(_BASE, "Cancer_Data.csv")   # Ruta al CSV
SCALER_PATH   = os.path.join(_BASE, "scaler.pkl")         # Archivo de salida del scaler
MODEL_PATH    = os.path.join(_BASE, "model_kmeans.pkl")   # Archivo de salida del modelo
N_CLUSTERS    = 2                       # K-Means con k=2
RANDOM_STATE  = 42                      # Semilla para reproducibilidad

# Las 8 variables seleccionadas por importancia (Random Forest)
FEATURES = [
    "perimeter_worst",
    "area_worst",
    "radius_worst",
    "concave_points_mean",
    "concave_points_worst",
    "concavity_mean",
    "perimeter_mean",
    "area_mean",
]

# Etiqueta real del dataset (solo se usa para verificar, NO para entrenar)
TARGET_COLUMN = "diagnosis"   # 'M' = Maligno, 'B' = Benigno


# ──────────────────────────────────────────────────────────────────────
#  PASO 1 — Cargar el dataset
# ──────────────────────────────────────────────────────────────────────
def cargar_dataset(ruta: str) -> pd.DataFrame:
    print(f"\n{'='*60}")
    print("  ONCOLAB AI — Entrenamiento y Exportación del Modelo")
    print(f"{'='*60}\n")

    if not os.path.exists(ruta):
        raise FileNotFoundError(
            f"❌  No se encontró el archivo '{ruta}'.\n"
            f"    Asegúrate de que Cancer_Data.csv esté en la misma carpeta."
        )

    df = pd.read_csv(ruta)
    print(f"✅  Dataset cargado correctamente.")
    print(f"    → Filas: {df.shape[0]}  |  Columnas: {df.shape[1]}")

    # Eliminar columnas innecesarias si existen (id, Unnamed)
    cols_a_eliminar = [c for c in df.columns if c.lower() in ('id', 'unnamed: 32')]
    if cols_a_eliminar:
        df.drop(columns=cols_a_eliminar, inplace=True)
        print(f"    → Columnas eliminadas: {cols_a_eliminar}")

    return df


# ──────────────────────────────────────────────────────────────────────
#  PASO 2 — Seleccionar las 8 características clave
# ──────────────────────────────────────────────────────────────────────
def seleccionar_features(df: pd.DataFrame) -> pd.DataFrame:
    # Verificar que las columnas existan
    faltantes = [f for f in FEATURES if f not in df.columns]
    if faltantes:
        raise ValueError(
            f"❌  Columnas no encontradas en el CSV: {faltantes}\n"
            f"    Verifica los nombres exactos en tu archivo."
        )

    X = df[FEATURES].copy()

    # Verificar valores nulos
    nulos = X.isnull().sum().sum()
    if nulos > 0:
        print(f"⚠️   Se encontraron {nulos} valores nulos. Se imputarán con la media.")
        X.fillna(X.mean(), inplace=True)

    print(f"\n✅  Features seleccionadas ({len(FEATURES)}):")
    for i, f in enumerate(FEATURES, 1):
        print(f"    {i}. {f}  →  min={X[f].min():.4f}  |  max={X[f].max():.4f}")

    return X


# ──────────────────────────────────────────────────────────────────────
#  PASO 3 — Escalar con MinMaxScaler
# ──────────────────────────────────────────────────────────────────────
def escalar_datos(X: pd.DataFrame):
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    print(f"\n✅  MinMaxScaler entrenado.")
    print(f"    → Rango de salida: [0.0, 1.0] para todas las variables")
    return scaler, X_scaled


# ──────────────────────────────────────────────────────────────────────
#  PASO 4 — Entrenar K-Means
# ──────────────────────────────────────────────────────────────────────
def entrenar_kmeans(X_scaled: np.ndarray):
    modelo = KMeans(
        n_clusters=N_CLUSTERS,
        init='k-means++',       # Inicialización inteligente
        n_init=10,              # 10 inicializaciones distintas
        max_iter=300,
        random_state=RANDOM_STATE,
    )
    modelo.fit(X_scaled)

    etiquetas    = modelo.labels_
    inercia      = modelo.inertia_
    sil_score    = silhouette_score(X_scaled, etiquetas)

    print(f"\n✅  KMeans(n_clusters={N_CLUSTERS}) entrenado.")
    print(f"    → Inercia (WCSS):       {inercia:.4f}")
    print(f"    → Silhouette Score:     {sil_score:.4f}")
    print(f"    → Iteraciones hechas:   {modelo.n_iter_}")
    print(f"    → Distribución de clusters:")
    unique, counts = np.unique(etiquetas, return_counts=True)
    for cl, cnt in zip(unique, counts):
        print(f"       Cluster {cl}: {cnt} muestras ({cnt/len(etiquetas)*100:.1f}%)")

    return modelo, etiquetas, sil_score


# ──────────────────────────────────────────────────────────────────────
#  PASO 5 — Verificar alineación Cluster → Diagnóstico real
# ──────────────────────────────────────────────────────────────────────
def verificar_alineacion(df: pd.DataFrame, etiquetas: np.ndarray) -> dict:
    """
    Compara los clusters con la etiqueta real 'diagnosis' del CSV.
    Determina qué cluster corresponde a Benigno y cuál a Maligno.
    IMPORTANTE: Esta info se usa solo para verificación/display.
    En Django usamos la convención Cluster 0 = Benigno / 1 = Maligno.
    Si el resultado se invierte, ajusta el mapeo en views.py.
    """
    if TARGET_COLUMN not in df.columns:
        print(f"\n⚠️   Columna '{TARGET_COLUMN}' no encontrada. Saltando verificación.")
        return {0: "Benigno", 1: "Maligno"}

    df_verif = df[[TARGET_COLUMN]].copy()
    df_verif['cluster'] = etiquetas

    print(f"\n{'─'*50}")
    print("  VERIFICACIÓN: Alineación Cluster ↔ Diagnóstico Real")
    print(f"{'─'*50}")

    mapeo = {}
    for cluster_id in [0, 1]:
        subset = df_verif[df_verif['cluster'] == cluster_id][TARGET_COLUMN]
        conteo = subset.value_counts()
        mayoria = conteo.idxmax()
        label = "Maligno" if mayoria == "M" else "Benigno"
        mapeo[cluster_id] = label
        pct = conteo[mayoria] / len(subset) * 100
        print(f"  Cluster {cluster_id}  →  Mayoría: '{mayoria}' ({pct:.1f}%)")
        print(f"             Diagnóstico asignado: {label}")

    print(f"\n  MAPEO FINAL:")
    for k, v in mapeo.items():
        print(f"  Cluster {k}  →  {v}")

    # Advertir si el mapeo difiere de la convención
    if mapeo.get(0) == "Maligno":
        print(
            "\n  ⚠️  ATENCIÓN: El Cluster 0 resultó MALIGNO en este entrenamiento."
            "\n      En views.py, cambia la condición a:"
            "\n      resultado = 'Benigno' if cluster == 1 else 'Maligno'"
        )

    return mapeo


# ──────────────────────────────────────────────────────────────────────
#  PASO 6 — Exportar modelos como .pkl
# ──────────────────────────────────────────────────────────────────────
def exportar_modelos(scaler, modelo):
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(modelo, MODEL_PATH)

    tamaño_scaler = os.path.getsize(SCALER_PATH) / 1024
    tamaño_modelo = os.path.getsize(MODEL_PATH)  / 1024

    print(f"\n{'='*60}")
    print("  ARCHIVOS EXPORTADOS EXITOSAMENTE")
    print(f"{'='*60}")
    print(f"  📦  {SCALER_PATH:<25} ({tamaño_scaler:.1f} KB)")
    print(f"  📦  {MODEL_PATH:<25} ({tamaño_modelo:.1f} KB)")
    print(f"\n  👉  Copia ambos archivos a la RAÍZ de tu proyecto Django:")
    print(f"      tu_proyecto/")
    print(f"      ├── scaler.pkl")
    print(f"      ├── model_kmeans.pkl")
    print(f"      ├── manage.py")
    print(f"      └── core/")
    print(f"{'='*60}\n")


# ──────────────────────────────────────────────────────────────────────
#  EJECUCIÓN PRINCIPAL
# ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        # 1. Cargar datos
        df = cargar_dataset(DATASET_PATH)

        # 2. Seleccionar features
        X = seleccionar_features(df)

        # 3. Escalar
        scaler, X_scaled = escalar_datos(X)

        # 4. Entrenar K-Means
        modelo, etiquetas, sil_score = entrenar_kmeans(X_scaled)

        # 5. Verificar alineación con etiquetas reales (informativo)
        mapeo = verificar_alineacion(df, etiquetas)

        # 6. Exportar .pkl
        exportar_modelos(scaler, modelo)

        print("✅  Proceso completado sin errores.")
        print(f"    Silhouette Score final: {sil_score:.4f}\n")

    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"\n❌  Error inesperado: {e}")
        raise
