import pytest
from app import predecir, app


# --- Tests de la función de clasificación ---

def test_no_enfermo():
    assert predecir(36.5, 1, 1) == "NO ENFERMO"


def test_enfermedad_leve():
    # score: temp=2, dolor=1, dias=1 → total=4
    assert predecir(38.0, 4, 3) == "ENFERMEDAD LEVE"


def test_enfermedad_aguda():
    # score: temp=4, dolor=2, dias=0 → total=6
    assert predecir(39.0, 6, 2) == "ENFERMEDAD AGUDA"


def test_enfermedad_cronica():
    # score: temp=6, dolor=3, dias=3 → total=12
    assert predecir(40.0, 9, 20) == "ENFERMEDAD CRÓNICA"


def test_temperatura_muy_alta_sola():
    # temp ≥ 39.5 → score=6 → AGUDA
    assert predecir(39.5, 0, 0) == "ENFERMEDAD AGUDA"


def test_solo_dolor_maximo():
    # dolor=10 → score=3 → LEVE
    assert predecir(36.0, 10, 0) == "ENFERMEDAD LEVE"


def test_score_limite_leve_aguda():
    # score exactamente 5 → LEVE (≤5), score 6 → AGUDA
    assert predecir(38.0, 5, 3) == "ENFERMEDAD LEVE"   # 2+2+1=5
    assert predecir(38.5, 5, 3) == "ENFERMEDAD AGUDA"  # 4+2+1=7


# --- Tests de la API HTTP ---

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_get_index_ok(client):
    r = client.get("/")
    assert r.status_code == 200


def test_post_valid_returns_resultado(client):
    r = client.post("/predecir", data={
        "temperatura": "38.0",
        "nivel_dolor": "4",
        "dias_sintomas": "3",
    })
    assert r.status_code == 200
    assert "LEVE" in r.data.decode("utf-8")


def test_post_temperatura_fuera_de_rango(client):
    r = client.post("/predecir", data={
        "temperatura": "45.0",
        "nivel_dolor": "5",
        "dias_sintomas": "3",
    })
    assert r.status_code == 200
    assert "Error" in r.data.decode("utf-8")


def test_post_dolor_fuera_de_rango(client):
    r = client.post("/predecir", data={
        "temperatura": "37.0",
        "nivel_dolor": "11",
        "dias_sintomas": "3",
    })
    assert r.status_code == 200
    assert "Error" in r.data.decode("utf-8")


def test_post_dias_negativos(client):
    r = client.post("/predecir", data={
        "temperatura": "37.0",
        "nivel_dolor": "5",
        "dias_sintomas": "-1",
    })
    assert r.status_code == 200
    assert "Error" in r.data.decode("utf-8")
