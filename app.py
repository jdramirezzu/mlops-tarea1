from flask import Flask, render_template, request

app = Flask(__name__)


def predecir(temperatura: float, nivel_dolor: int, dias_sintomas: int) -> str:
    """
    Simula un modelo de clasificacion de enfermedad.
    Retorna uno de: NO ENFERMO, ENFERMEDAD LEVE, ENFERMEDAD AGUDA, ENFERMEDAD CRONICA.

    Parametros:
      - temperatura:    temperatura corporal en grados Celsius
      - nivel_dolor:    nivel de dolor autoreportado de 0 a 10
      - dias_sintomas:  cantidad de dias con sintomas presentes
    """
    score = 0

    if temperatura >= 39.5:
        score += 6
    elif temperatura >= 38.5:
        score += 4
    elif temperatura >= 37.5:
        score += 2

    if nivel_dolor >= 8:
        score += 3
    elif nivel_dolor >= 5:
        score += 2
    elif nivel_dolor >= 3:
        score += 1

    if dias_sintomas > 14:
        score += 3
    elif dias_sintomas >= 8:
        score += 2
    elif dias_sintomas >= 3:
        score += 1

    if score <= 2:
        return "NO ENFERMO"
    elif score <= 5:
        return "ENFERMEDAD LEVE"
    elif score <= 8:
        return "ENFERMEDAD AGUDA"
    else:
        return "ENFERMEDAD CRÓNICA"


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/predecir", methods=["POST"])
def predecir_endpoint():
    try:
        temperatura = float(request.form["temperatura"])
        nivel_dolor = int(request.form["nivel_dolor"])
        dias_sintomas = int(request.form["dias_sintomas"])

        if not (35.0 <= temperatura <= 42.0):
            raise ValueError("Temperatura fuera de rango (35-42 °C).")
        if not (0 <= nivel_dolor <= 10):
            raise ValueError("Nivel de dolor debe estar entre 0 y 10.")
        if dias_sintomas < 0:
            raise ValueError("Los días de síntomas no pueden ser negativos.")

        resultado = predecir(temperatura, nivel_dolor, dias_sintomas)
        return render_template("index.html", resultado=resultado)

    except (ValueError, KeyError) as e:
        return render_template("index.html", error=str(e))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
