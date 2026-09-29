"""
tests/test_gastos.py

Tests de no-regresión para el menú de gastos.py.
"""
import json

import pytest

import gastos

SALIR = "8"

GASTOS_BASE = [
    {"descripcion": "Supermercado", "cantidad": 50.25, "categoria": "Alimentacion", "fecha": "2026-09-03"},
    {"descripcion": "Metro",        "cantidad": 12.50, "categoria": "Transporte",   "fecha": "2026-09-10"},
    {"descripcion": "Cine",         "cantidad": 30.00, "categoria": "Ocio",         "fecha": "2026-09-15"},
]


# ---------------------------------------------------------------------------
# Fixtures y helpers
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def carpeta_temporal(tmp_path, monkeypatch):
    """Cada test trabaja en una carpeta vacía con su propio gastos.json."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def ejecutar(monkeypatch, entradas):
    it = iter(entradas)
    monkeypatch.setattr("builtins.input", lambda _="": next(it))
    gastos.main()


def leer_json(carpeta):
    return json.loads((carpeta / "gastos.json").read_text(encoding="utf-8"))


def crear_json(carpeta, datos=None):
    """Escribe gastos.json con los datos dados (o GASTOS_BASE por defecto)."""
    if datos is None:
        datos = GASTOS_BASE
    (carpeta / "gastos.json").write_text(json.dumps(datos), encoding="utf-8")


# Secuencia reutilizable para añadir un gasto válido (categoría 3 = Ocio)
ANADIR_OK = ["1", "Café", "2.50", "3", "2026-09-01"]


# ---------------------------------------------------------------------------
# Añadir gasto
# ---------------------------------------------------------------------------

def test_anadir_gasto_valido(monkeypatch, carpeta_temporal):
    ejecutar(monkeypatch, ANADIR_OK + [SALIR])
    datos = leer_json(carpeta_temporal)
    assert datos == [
        {"descripcion": "Café", "cantidad": 2.5, "categoria": "Ocio", "fecha": "2026-09-01"}
    ]


def test_anadir_cantidad_invalida(monkeypatch, capsys):
    ejecutar(monkeypatch, ["1", "Café", "abc", SALIR])
    assert "se esperaba un número" in capsys.readouterr().out


@pytest.mark.parametrize(
    "entradas, mensaje",
    [
        (["1", "Café", "2.5", "9"], "categoría no válida"),   # categoría fuera de rango
        (["1", "Café", "2.5", "x"], "categoría no válida"),   # categoría no numérica
    ],
)
def test_anadir_gasto_categoria_invalida(monkeypatch, carpeta_temporal, capsys, entradas, mensaje):
    ejecutar(monkeypatch, entradas + [SALIR])
    assert mensaje in capsys.readouterr().out
    assert not (carpeta_temporal / "gastos.json").exists()


# ---------------------------------------------------------------------------
# Listar gastos
# ---------------------------------------------------------------------------

def test_listar_sin_gastos(monkeypatch, capsys):
    ejecutar(monkeypatch, ["2", SALIR])
    assert "No hay gastos registrados" in capsys.readouterr().out


def test_listar_con_gastos(monkeypatch, capsys):
    ejecutar(monkeypatch, ANADIR_OK + ["2", SALIR])
    salida = capsys.readouterr().out
    assert "Café" in salida and "2.50" in salida


def test_cargar_gastos_existentes(monkeypatch, carpeta_temporal, capsys):
    previo = [{"descripcion": "Taxi", "cantidad": 10.0, "categoria": "Transporte", "fecha": "2026-01-02"}]
    (carpeta_temporal / "gastos.json").write_text(json.dumps(previo), encoding="utf-8")
    ejecutar(monkeypatch, ["2", SALIR])
    assert "Taxi" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Eliminar gasto
# ---------------------------------------------------------------------------

def test_eliminar_gasto(monkeypatch, carpeta_temporal, capsys):
    ejecutar(monkeypatch, ANADIR_OK + ["3", "1", SALIR])
    assert leer_json(carpeta_temporal) == []
    assert "Gasto eliminado" in capsys.readouterr().out


@pytest.mark.parametrize("numero, mensaje", [
    ("5", "fuera de rango"),
    ("x", "se esperaba un número entero"),
])
def test_eliminar_entradas_invalidas(monkeypatch, capsys, numero, mensaje):
    ejecutar(monkeypatch, ANADIR_OK + ["3", numero, SALIR])
    assert mensaje in capsys.readouterr().out


def test_eliminar_sin_gastos(monkeypatch, capsys):
    ejecutar(monkeypatch, ["3", SALIR])
    assert "No hay gastos registrados" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Opción 4: Total mensual
# ---------------------------------------------------------------------------

def test_total_mensual(monkeypatch, carpeta_temporal, capsys):
    crear_json(carpeta_temporal)
    ejecutar(monkeypatch, ["4", "2026", "9", SALIR])
    assert "92.75" in capsys.readouterr().out


def test_total_mensual_mes_invalido(monkeypatch, capsys):
    ejecutar(monkeypatch, ["4", "2026", "13", SALIR])
    assert "entre 1 y 12" in capsys.readouterr().out


def test_total_mensual_anio_no_numerico(monkeypatch, capsys):
    ejecutar(monkeypatch, ["4", "abc", "9", SALIR])
    assert "se esperaba un número entero" in capsys.readouterr().out


def test_total_mensual_mes_no_numerico(monkeypatch, capsys):
    ejecutar(monkeypatch, ["4", "2026", "x", SALIR])
    assert "se esperaba un número entero" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Opción 5: Total por categoría
# ---------------------------------------------------------------------------

def test_total_por_categoria_global(monkeypatch, carpeta_temporal, capsys):
    crear_json(carpeta_temporal)
    ejecutar(monkeypatch, ["5", "n", SALIR])
    salida = capsys.readouterr().out
    assert "Alimentacion" in salida
    assert "50.25" in salida


def test_total_por_categoria_con_mes(monkeypatch, carpeta_temporal, capsys):
    crear_json(carpeta_temporal)
    ejecutar(monkeypatch, ["5", "s", "2026", "9", SALIR])
    salida = capsys.readouterr().out
    assert "Alimentacion" in salida


def test_total_por_categoria_sin_gastos(monkeypatch, capsys):
    ejecutar(monkeypatch, ["5", "n", SALIR])
    assert "No hay gastos registrados" in capsys.readouterr().out


def test_total_por_categoria_mes_invalido(monkeypatch, capsys):
    ejecutar(monkeypatch, ["5", "s", "2026", "13", SALIR])
    assert "entre 1 y 12" in capsys.readouterr().out


def test_total_por_categoria_mes_no_numerico(monkeypatch, capsys):
    ejecutar(monkeypatch, ["5", "s", "2026", "x", SALIR])
    assert "se esperaba un número entero" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Opción 6: Filtrar por categoría
# ---------------------------------------------------------------------------

def test_filtrar_por_categoria(monkeypatch, carpeta_temporal, capsys):
    crear_json(carpeta_temporal)
    ejecutar(monkeypatch, ["6", "1", SALIR])   # 1 = Alimentacion
    assert "Supermercado" in capsys.readouterr().out


def test_filtrar_por_categoria_sin_resultados(monkeypatch, carpeta_temporal, capsys):
    crear_json(carpeta_temporal)
    ejecutar(monkeypatch, ["6", "4", SALIR])   # 4 = Salud, no hay gastos
    assert "No hay gastos en esa categoría" in capsys.readouterr().out


def test_filtrar_por_categoria_invalida(monkeypatch, capsys):
    ejecutar(monkeypatch, ["6", "9", SALIR])
    assert "categoría no válida" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Opción 7: Ordenar por importe
# ---------------------------------------------------------------------------

def test_ordenar_descendente(monkeypatch, carpeta_temporal, capsys):
    crear_json(carpeta_temporal)
    ejecutar(monkeypatch, ["7", "n", SALIR])
    salida = capsys.readouterr().out
    assert "descendente" in salida
    pos_50 = salida.find("50.25")
    pos_12 = salida.find("12.50")
    assert pos_50 < pos_12   # el mayor aparece antes


def test_ordenar_ascendente(monkeypatch, carpeta_temporal, capsys):
    crear_json(carpeta_temporal)
    ejecutar(monkeypatch, ["7", "s", SALIR])
    salida = capsys.readouterr().out
    assert "ascendente" in salida
    pos_12 = salida.find("12.50")
    pos_50 = salida.find("50.25")
    assert pos_12 < pos_50   # el menor aparece antes


def test_ordenar_sin_gastos(monkeypatch, capsys):
    ejecutar(monkeypatch, ["7", "n", SALIR])
    assert "No hay gastos registrados" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Opción no válida
# ---------------------------------------------------------------------------

def test_opcion_no_valida(monkeypatch, capsys):
    ejecutar(monkeypatch, ["99", SALIR])
    assert "Opción no válida" in capsys.readouterr().out


def test_total_por_categoria_anio_no_numerico(monkeypatch, capsys):
    ejecutar(monkeypatch, ["5", "s", "abc", "9", SALIR])
    assert "se esperaba un número entero" in capsys.readouterr().out
