# Pipeline de MLOps — Predicción de Enfermedades

## Descripción del problema

Se requiere un sistema capaz de clasificar el estado de salud de un paciente en una de cuatro categorías (`NO ENFERMO`, `ENFERMEDAD LEVE`, `ENFERMEDAD AGUDA`, `ENFERMEDAD CRÓNICA`) a partir de síntomas observables. El sistema debe funcionar tanto para **enfermedades comunes** (abundancia de datos) como para **enfermedades huérfanas** (escasez de datos), lo cual introduce desafíos importantes en el diseño del pipeline.

---

## Diagrama general del pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PIPELINE DE MLOps                               │
│                                                                              │
│  ┌─────────┐  ┌──────────────┐  ┌────────────┐  ┌────────┐  ┌───────────┐  │
│  │ DISEÑO  │─▶│    DATOS     │─▶│  MODELADO  │─▶│ CI/CD  │─▶│PRODUCCIÓN │  │
│  └─────────┘  └──────────────┘  └────────────┘  └────────┘  └─────┬─────┘  │
│                      ▲                                              │        │
│                      │                                              ▼        │
│                      │                                       ┌───────────┐  │
│                      │                                       │ MONITOREO │  │
│                      │                                       │ Data drift│  │
│                      │                                       │Model drift│  │
│                      │                                       └─────┬─────┘  │
│                      │                                             │        │
│                      └──────────── Reentrenamiento ────────────────┘        │
│                          (periódico o por alerta de drift)                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Diseño

### 1.1 Restricciones y limitaciones

| Restricción | Descripción |
|---|---|
| **Privacidad** | Los datos de pacientes están protegidos por regulaciones (GDPR, leyes de salud locales). Se requiere anonimización y manejo seguro. |
| **Desbalance de clases** | Las enfermedades huérfanas tienen muy pocos casos. Los modelos tenderán a ignorar estas clases. |
| **Interpretabilidad** | En el dominio médico, el médico debe poder entender por qué el modelo tomó una decisión. No alcanza con alta exactitud. |
| **Calidad del etiquetado** | Las etiquetas deben ser validadas por especialistas médicos, lo cual es costoso y lento. |
| **Generalización** | Un modelo entrenado en una región puede no funcionar bien en otra por diferencias de población. |

### 1.2 Tipos de datos disponibles

- **Síntomas observables**: temperatura corporal, nivel de dolor, duración de síntomas *(los 3 usados en la solución Docker)*
- **Datos de laboratorio**: hemograma, glucemia, marcadores inflamatorios
- **Datos clínicos**: historial de enfermedades previas, medicamentos actuales, edad, sexo
- **Imágenes médicas** (opcional): radiografías, ecografías (requieren modelos de visión)
- **Datos genómicos** (especialmente relevante para enfermedades huérfanas)

---

## 2. Datos

### 2.1 Fuentes de datos

```
Fuentes de datos
│
├── Enfermedades comunes
│   ├── Registros hospitalarios / Historia clínica electrónica (HCE)
│   ├── Bases de datos públicas: UCI ML Repository, PhysioNet
│   └── Datos propios recolectados en consulta
│
└── Enfermedades huérfanas
    ├── Orphanet (base de datos europea de enfermedades raras)
    ├── NIH Rare Diseases Clinical Research Network
    ├── Publicaciones científicas (extracción manual/NLP)
    └── Datos sintéticos generados (augmentation)
```

### 2.2 Preprocesamiento

1. **Limpieza**: eliminación de duplicados, manejo de valores faltantes (imputación o descarte según el caso).
2. **Normalización**: escalar variables continuas como temperatura y frecuencia cardíaca a rangos comparables.
3. **Codificación**: convertir variables categóricas (ej. tipo de síntoma) a representaciones numéricas.
4. **Feature engineering**: crear variables derivadas, como la combinación de síntomas que históricamente correlacionan con ciertas enfermedades.
5. **Balanceo de clases**: aplicar técnicas como **SMOTE** (oversampling sintético) para las clases minoritarias (enfermedades huérfanas).

### 2.3 Gestión de datos

- Los datos crudos se almacenan en un **data lake** (sin transformar).
- Los datos preprocesados se versionan junto al código en el repositorio para garantizar reproducibilidad.
- Se mantiene un **catálogo de datos** con metadata: origen, fecha, versión, esquema.

---

## 3. Modelado

### 3.1 Modelos candidatos

| Escenario | Modelos recomendados | Justificación |
|---|---|---|
| Enfermedades comunes (muchos datos) | Random Forest, XGBoost, Red neuronal MLP | Alta capacidad, funcionan bien con muchos datos |
| Enfermedades huérfanas (pocos datos) | Modelos con regularización fuerte, **Few-Shot Learning**, **Transfer Learning** | Evitan sobreajuste con datos escasos |
| Ambos escenarios combinados | Ensemble o modelo con cabezas especializadas por enfermedad | Aprovecha datos de enfermedades comunes para mejorar raras |

> **Nota sobre la solución actual**: La función implementada en `app.py` es una aproximación basada en reglas (scoring manual). En un pipeline real, esta función sería reemplazada por un modelo entrenado que se carga desde un archivo (`.pkl`, `.onnx`, etc.) y produce la misma interfaz de salida.

### 3.2 Validación y evaluación

- **Estrategia**: validación cruzada estratificada (k-fold) para respetar la distribución de clases.
- **Métricas**:
  - **F1-score macro**: penaliza igualmente errores en clases raras y comunes.
  - **Sensibilidad (Recall)**: crítica en medicina para no perder casos positivos.
  - **AUC-ROC**: evalúa la capacidad discriminativa general del modelo.
  - **Matriz de confusión**: identificar qué tipos de error comete el modelo.
- **Validación clínica**: revisión de predicciones por médicos antes del despliegue.

---

## 4. Producción

### 4.1 Despliegue

El modelo entrenado se empaqueta en un contenedor Docker, tal como se implementa en la **Parte 2** de esta tarea. El flujo de despliegue es:

```
Modelo entrenado (.pkl / .onnx)
         │
         ▼
  Aplicación Flask (app.py)
         │
         ▼
  Imagen Docker (Dockerfile)
         │
         ▼
  Contenedor corriendo en el equipo del médico
  → Interfaz web en http://localhost:5000
```

En un entorno más escalable, el contenedor podría desplegarse en la nube (AWS ECS, Google Cloud Run, Azure Container Instances) con un balanceador de carga para múltiples usuarios simultáneos.

---

### 4.2 CI/CD con GitHub Actions

Se implementa un pipeline de integración y despliegue continuo usando **GitHub Actions**, organizado en torno a una estrategia de ramas clara y tres workflows especializados.

#### Estrategia de ramas (Branching Strategy)

```
  main  ──────────────────────────────────────  (producción estable)
    │  ↑ PR aprobado + todos los gates en verde
  develop ──────────────────────────────────── (integración continua)
      │  ↑ PR aprobado + CI verde
      ├── feature/*     nuevas características del modelo o servicio
      ├── hotfix/*      correcciones urgentes directas a producción
      └── experiment/*  exploración de nuevos algoritmos o datos
```

Ningún commit va directo a `main` ni a `develop`: todo pasa por Pull Request. El CI debe estar completamente verde antes de que el merge sea posible.

---

#### Workflow 1 — Integración Continua (`ci.yml`)

**Trigger:** `push` o `pull_request` en cualquier rama.  
**Propósito:** garantizar que cada cambio pasa lint, tests y que la imagen Docker compila correctamente antes de poder mergearse.

```
  push / pull_request  ──────────────────────────────────────────────────────
  │
  ├──▶ [job: lint]
  │    └─ flake8 app.py
  │         └── FAIL ──▶ ✗ PR bloqueado (no se puede mergear)
  │
  ├──▶ [job: test]  (necesita: lint ✓)
  │    └─ pytest tests/ -v
  │         └── FAIL ──▶ ✗ PR bloqueado
  │
  └──▶ [job: docker-build]  (necesita: test ✓)
       └─ docker build . (sin push, solo verifica que compila)
            └── FAIL ──▶ ✗ PR bloqueado

  Solo si los 3 jobs son ✓ el PR puede mergearse.
```

---

#### Workflow 2 — Despliegue Continuo (`cd.yml`)

**Trigger:** `push` a rama `main` (es decir, cada merge aprobado).  
**Propósito:** construir la imagen definitiva, publicarla en el registry, validarla en staging y desplegarla en producción con aprobación humana.

```
  merge a main
  │
  ▼
  [job: build-push]
  └─ docker build + push → ghcr.io/usuario/repo:sha  y  :latest
  │
  ▼
  [job: smoke-test]
  └─ docker run (imagen recién publicada)
     curl http://localhost:5000  →  ¿responde 200?
     │
     ├── FAIL ──▶ ✗ pipeline se detiene
     │            notificación al equipo
     │            imagen anterior sigue en producción (rollback implícito)
     │
     └── OK ──▶ continúa
  │
  ▼
  [job: deploy-production]  ← environment: production
  └─ requiere aprobación manual de un revisor en GitHub
     (líder técnico o médico responsable)
     │
     ├── Aprobado ──▶ docker pull + restart del servicio en servidor
     │                │
     │                └── FAIL ──▶ rollback automático a imagen anterior
     │
     └── Rechazado ──▶ pipeline cancelado, sin cambios en producción
```

La imagen se identifica con el SHA del commit, lo que permite referenciar exactamente qué versión está en producción y hacer rollback a cualquier versión anterior publicada en el registry.

---

#### Workflow 3 — Reentrenamiento del Modelo (`model-retrain.yml`)

**Trigger:** `schedule` (mensual, ej. `cron: '0 6 1 * *'`) **o** disparo manual / alerta de drift desde el sistema de monitoreo.  
**Propósito:** actualizar el modelo con datos nuevos si y solo si supera el umbral de calidad definido.

```
  schedule mensual  /  alerta de drift detectada
  │
  ▼
  [job: validate-data]
  └─ verificar calidad y volumen de datos nuevos acumulados
     │
     ├── FAIL ──▶ notificación al equipo, pipeline se detiene
     │            (no se reentrena con datos insuficientes o corruptos)
     └── OK ──▶ continúa
  │
  ▼
  [job: train]
  └─ entrenar modelo con datos nuevos + datos históricos versionados
  │
  ▼
  [job: evaluate]  ← gate de calidad
  └─ calcular F1-score macro en conjunto de validación
     │
     ├── F1 < umbral ──▶ ✗ modelo no promovido
     │                    alerta al equipo de ML con métricas del run
     └── F1 ≥ umbral ──▶ continúa
  │
  ▼
  [job: register]
  └─ push del modelo al model registry (MLflow / DVC)
     versión y métricas registradas con trazabilidad completa
  │
  ▼
  [job: update-service]
  └─ actualizar modelo en la imagen Docker
     ──▶ dispara el Workflow CD automáticamente
         (build-push → smoke-test → deploy-production)
```

---

#### Diagrama integrado: CI/CD dentro del pipeline MLOps

```
  Desarrollo  ──▶  Pull Request  ──▶  CI (lint + test + build)  ──▶  Merge
       │                                                                │
       │                                                                ▼
  experiment/*                                              CD (build-push)
       │                                                                │
       ▼                                                                ▼
  [Reentrenamiento]                                         Smoke Test en Staging
  validate → train                                                      │
       │                                                     OK         │    FAIL
       ▼                                                     │          │      │
  evaluate (gate F1)  ──FAIL──▶  alerta, sin deploy          ▼          │    rollback
       │ OK                                          Aprobación manual   │
       ▼                                                      │          │
  model registry  ──▶  update-service  ──▶  CD ──────────────▼          │
                                                     Deploy Producción ◀─┘
```

---

## 5. Monitoreo y mantenimiento

### 5.1 ¿Por qué monitorear?

Los modelos de ML degradan su rendimiento con el tiempo porque:
- Los patrones de síntomas cambian (ej. nuevas variantes de enfermedades).
- La distribución de pacientes atendidos cambia (diferente región, edad, etc.).
- Aparecen nuevas enfermedades o criterios diagnósticos se actualizan.

### 5.2 Qué monitorear

| Tipo de monitoreo | Descripción |
|---|---|
| **Data drift** | Detectar si la distribución de los datos de entrada cambió respecto al entrenamiento |
| **Model drift** | Detectar caída en métricas de rendimiento con datos recientes etiquetados |
| **Infraestructura** | Latencia de respuesta, disponibilidad del servicio, uso de recursos |
| **Feedback médico** | Registrar casos donde el médico corrigió la predicción del modelo |

### 5.3 Reentrenamiento

- Se propone un ciclo de reentrenamiento **periódico** (ej. mensual) con los nuevos datos acumulados.
- Si se detecta degradación abrupta del modelo, se puede disparar un reentrenamiento **por alerta**.
- Los datos de corrección del médico (feedback) son especialmente valiosos para mejorar el modelo.

---

## Resumen visual del pipeline completo

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  [Fuentes de datos]                                                      │
│  Hospitales / Bases públicas / Datos sintéticos                          │
│           │                                                              │
│           ▼                                                              │
│  [Ingesta y almacenamiento]                                              │
│  Data Lake → Versionado con DVC                                          │
│           │                                                              │
│           ▼                                                              │
│  [Preprocesamiento]                                                      │
│  Limpieza → Normalización → SMOTE → Feature Engineering                  │
│           │                                                              │
│           ▼                                                              │
│  [Entrenamiento]                                                         │
│  Modelos comunes: XGBoost / MLP                                          │
│  Modelos huérfanos: Few-Shot / Transfer Learning                         │
│           │                                                              │
│           ▼                                                              │
│  [Evaluación]  ← gate: F1 ≥ umbral para continuar                       │
│  F1 macro / Recall / AUC-ROC / Validación clínica                       │
│           │                                                              │
│           ▼                                                              │
│  [CI/CD — GitHub Actions]                                                │
│  lint → tests → docker build  (CI, en cada PR)                          │
│  build-push → smoke test → aprobación → producción  (CD, en cada merge) │
│           │  ← gate: smoke test OK + aprobación manual                  │
│           ▼                                                              │
│  [Despliegue en Producción]                                              │
│  Docker (Flask API + Interfaz web) → localhost:5000 / cloud              │
│           │                                                              │
│           ▼                                                              │
│  [Monitoreo]                                                             │
│  Data drift / Model drift / Latencia / Feedback médico                   │
│           │                                                              │
│           └──────────────── Reentrenamiento ─────────────────────────── │
│                (periódico o por alerta) → vuelve a Entrenamiento         │
└──────────────────────────────────────────────────────────────────────────┘
```
