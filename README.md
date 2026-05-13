# Predictor de Enfermedades — Servicio Docker
## Maestria en inteligencia artificial aplicada

## Presentado por: JUAN DIEGO RAMIREZ - JUAN JOSE AGUADO

Servicio web que simula un modelo de clasificación de enfermedades a partir de síntomas del paciente. El médico ingresa tres valores y el sistema retorna uno de los siguientes estados:

- **NO ENFERMO**
- **ENFERMEDAD LEVE**
- **ENFERMEDAD AGUDA**
- **ENFERMEDAD CRÓNICA**

---

## Lógica de clasificación

La función `predecir` asigna puntajes a cada parámetro de entrada y los suma para determinar el estado:

| Parámetro | Valor | Puntaje |
|---|---|---|
| Temperatura (°C) | < 37.5 | 0 |
| | 37.5 – 38.4 | 2 |
| | 38.5 – 39.4 | 4 |
| | ≥ 39.5 | 6 |
| Nivel de dolor (0-10) | 0 – 2 | 0 |
| | 3 – 4 | 1 |
| | 5 – 7 | 2 |
| | 8 – 10 | 3 |
| Días con síntomas | 0 – 2 | 0 |
| | 3 – 7 | 1 |
| | 8 – 14 | 2 |
| | > 14 | 3 |

| Puntaje total | Diagnóstico |
|---|---|
| 0 – 2 | NO ENFERMO |
| 3 – 5 | ENFERMEDAD LEVE |
| 6 – 8 | ENFERMEDAD AGUDA |
| ≥ 9 | ENFERMEDAD CRÓNICA |

---

## Estructura del proyecto

```
.
├── app.py               # Aplicación Flask y función de predicción
├── requirements.txt     # Dependencias Python
├── Dockerfile           # Definición de la imagen Docker
├── README.md            # Este archivo
└── templates/
    └── index.html       # Interfaz web
```

---

## Requisitos previos

- [Docker](https://www.docker.com/) instalado y corriendo.

---

## Construcción de la imagen

Desde la carpeta raíz del proyecto (donde está el `Dockerfile`), ejecutar:

```bash
docker build -t predictor-enfermedades .
```

---

## Ejecución del contenedor

```bash
docker run -p 5000:5000 predictor-enfermedades
```

El servicio quedará disponible en: [http://localhost:5000](http://localhost:5000)

---

## Uso

1. Abrir el navegador en `http://localhost:5000`.
2. Ingresar los tres valores del paciente:
   - **Temperatura corporal** en °C (ej: `38.5`)
   - **Nivel de dolor** del 0 al 10 (ej: `6`)
   - **Días con síntomas** (ej: `5`)
3. Presionar **"Obtener diagnóstico"**.
4. El sistema mostrará el estado clasificado.

---

## Ejemplos de resultados

| Temperatura | Dolor | Días | Resultado |
|---|---|---|---|
| 36.5 | 1 | 1 | NO ENFERMO |
| 38.0 | 4 | 3 | ENFERMEDAD LEVE |
| 39.0 | 6 | 2 | ENFERMEDAD AGUDA |
| 40.0 | 9 | 20 | ENFERMEDAD CRÓNICA |

---

## Detener el contenedor

```bash
docker stop $(docker ps -q --filter ancestor=predictor-enfermedades)
```
