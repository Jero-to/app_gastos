"""
tests/test_filtros.py

Tests unitarios (ejemplo-based) y de propiedad (hypothesis) para filtros.py.
"""
import sys
import os

# Asegura que pytest encuentre filtros.py desde este directorio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import copy
import pytest
from hypothesis import given, assume, settings
from hypothesis import strategies as st

import filtros
from filtros import (
    total_mensual,
    total_por_categoria,
    filtrar_por_categoria,
    ordenar_por_importe,
    CATEGORIAS_VALIDAS,
)


# ---------------------------------------------------------------------------
# Fixtures / datos de apoyo
# ---------------------------------------------------------------------------

GASTOS_EJEMPLO = [
    {"descripcion": "Mercado",     "cantidad": 50.00,  "categoria": "Alimentacion", "fecha": "2024-01-15"},
    {"descripcion": "Bus mensual", "cantidad": 30.00,  "categoria": "Transporte",   "fecha": "2024-01-20"},
    {"descripcion": "Cine",        "cantidad": 12.50,  "categoria": "Ocio",         "fecha": "2024-01-25"},
    {"descripcion": "Farmacia",    "cantidad": 18.75,  "categoria": "Salud",        "fecha": "2024-02-05"},
    {"descripcion": "Supermercado","cantidad": 65.33,  "categoria": "Alimentacion", "fecha": "2024-02-10"},
    {"descripcion": "Gasolina",    "cantidad": 40.00,  "categoria": "Transporte",   "fecha": "2024-03-01"},
]


# ---------------------------------------------------------------------------
# Helpers de Hypothesis
# ---------------------------------------------------------------------------

# Estrategia para generar un gasto válido
_gasto_st = st.fixed_dictionaries({
    "descripcion": st.text(min_size=1, max_size=50),
    "cantidad":    st.floats(min_value=0.01, max_value=10_000.0,
                             allow_nan=False, allow_infinity=False),
    "categoria":   st.sampled_from(sorted(CATEGORIAS_VALIDAS)),
    "fecha":       st.builds(
        lambda y, m, d: f"{y:04d}-{m:02d}-{d:02d}",
        y=st.integers(min_value=2000, max_value=2100),
        m=st.integers(min_value=1,    max_value=12),
        d=st.integers(min_value=1,    max_value=28),
    ),
})

_lista_gastos_st = st.lists(_gasto_st, min_size=0, max_size=20)
_categoria_valida_st = st.sampled_from(sorted(CATEGORIAS_VALIDAS))
_anio_st  = st.integers(min_value=2000, max_value=2100)
_mes_st   = st.integers(min_value=1,    max_value=12)


# ===========================================================================
# Tests ejemplo-based (pytest)
# ===========================================================================

# --- total_mensual ---

def test_total_mensual_con_gastos():
    """Suma correctamente los gastos de enero 2024."""
    resultado = total_mensual(GASTOS_EJEMPLO, 2024, 1)
    # 50.00 + 30.00 + 12.50 = 92.50
    assert resultado == 92.50


def test_total_mensual_mes_sin_gastos():
    """Devuelve 0.0 cuando no hay gastos en el mes solicitado."""
    resultado = total_mensual(GASTOS_EJEMPLO, 2024, 6)
    assert resultado == 0.0


def test_total_mensual_redondeo():
    """El resultado está redondeado a exactamente 2 decimales."""
    gastos = [
        {"descripcion": "A", "cantidad": 0.1,  "categoria": "Ocio", "fecha": "2024-05-01"},
        {"descripcion": "B", "cantidad": 0.2,  "categoria": "Ocio", "fecha": "2024-05-02"},
    ]
    # 0.1 + 0.2 puede dar 0.30000000000000004 en punto flotante sin redondeo
    resultado = total_mensual(gastos, 2024, 5)
    assert resultado == round(0.1 + 0.2, 2)
    assert isinstance(resultado, float)


# --- total_por_categoria ---

def test_total_por_categoria_global():
    """Agrupa todos los gastos por categoría correctamente."""
    resultado = total_por_categoria(GASTOS_EJEMPLO)
    assert resultado["Alimentacion"] == round(50.00 + 65.33, 2)  # 115.33
    assert resultado["Transporte"]   == round(30.00 + 40.00, 2)  # 70.00
    assert resultado["Ocio"]         == 12.50
    assert resultado["Salud"]        == 18.75
    assert "Otros" not in resultado  # sin gastos en Otros


def test_total_por_categoria_con_mes():
    """Restringe el agrupamiento al mes indicado."""
    resultado = total_por_categoria(GASTOS_EJEMPLO, anio=2024, mes=1)
    assert resultado == {
        "Alimentacion": 50.00,
        "Transporte":   30.00,
        "Ocio":         12.50,
    }


def test_total_por_categoria_omite_vacias():
    """No incluye categorías sin gastos (sin entradas con valor 0.0)."""
    gastos = [
        {"descripcion": "X", "cantidad": 10.0, "categoria": "Salud", "fecha": "2024-01-01"},
    ]
    resultado = total_por_categoria(gastos)
    assert "Otros"        not in resultado
    assert "Ocio"         not in resultado
    assert "Transporte"   not in resultado
    assert "Alimentacion" not in resultado
    assert resultado.get("Salud") == 10.0


# --- filtrar_por_categoria ---

def test_filtrar_por_categoria_devuelve_correctos():
    """Devuelve únicamente los gastos de la categoría indicada."""
    resultado = filtrar_por_categoria(GASTOS_EJEMPLO, "Alimentacion")
    assert len(resultado) == 2
    assert all(g["categoria"] == "Alimentacion" for g in resultado)


def test_filtrar_por_categoria_lista_vacia():
    """Devuelve lista vacía cuando no hay gastos de esa categoría."""
    resultado = filtrar_por_categoria(GASTOS_EJEMPLO, "Otros")
    assert resultado == []


def test_filtrar_por_categoria_preserva_orden():
    """El orden de los gastos resultantes coincide con el orden original."""
    resultado = filtrar_por_categoria(GASTOS_EJEMPLO, "Transporte")
    indices_originales = [
        i for i, g in enumerate(GASTOS_EJEMPLO) if g["categoria"] == "Transporte"
    ]
    # Los gastos de Transporte deben aparecer en el mismo orden relativo
    for pos, gasto in enumerate(resultado):
        assert gasto is GASTOS_EJEMPLO[indices_originales[pos]]


# --- ordenar_por_importe ---

def test_ordenar_descendente_por_defecto():
    """Sin argumento, ordena de mayor a menor."""
    resultado = ordenar_por_importe(GASTOS_EJEMPLO)
    cantidades = [g["cantidad"] for g in resultado]
    assert cantidades == sorted(cantidades, reverse=True)


def test_ordenar_ascendente():
    """Con ascendente=True, ordena de menor a mayor."""
    resultado = ordenar_por_importe(GASTOS_EJEMPLO, ascendente=True)
    cantidades = [g["cantidad"] for g in resultado]
    assert cantidades == sorted(cantidades)


def test_ordenar_no_modifica_original():
    """La lista original no debe verse afectada tras la llamada."""
    original = copy.deepcopy(GASTOS_EJEMPLO)
    ordenar_por_importe(GASTOS_EJEMPLO)
    assert GASTOS_EJEMPLO == original


def test_ordenar_lista_vacia():
    """Devuelve lista vacía cuando la entrada está vacía."""
    assert ordenar_por_importe([]) == []


# ===========================================================================
# Tests de propiedad (hypothesis)
# ===========================================================================

@given(_lista_gastos_st, _anio_st, _mes_st)
@settings(max_examples=200)
def test_prop_total_mensual_igual_suma_manual(gastos, anio, mes):
    """
    **Validates: Requirements 1.1**

    P1 – Invariante de suma:
    total_mensual debe ser igual a la suma manual de cantidades del mes,
    redondeada a 2 decimales.
    """
    esperado = round(
        sum(g["cantidad"] for g in gastos if filtros._misma_fecha(g["fecha"], anio, mes)),
        2,
    )
    assert total_mensual(gastos, anio, mes) == esperado


@given(_lista_gastos_st, _categoria_valida_st)
@settings(max_examples=200)
def test_prop_filtrar_tamano_menor_o_igual(gastos, categoria):
    """
    **Validates: Requirements 3.1**

    P2 – Invariante de tamaño:
    La longitud del resultado de filtrar_por_categoria es <= longitud original.
    """
    resultado = filtrar_por_categoria(gastos, categoria)
    assert len(resultado) <= len(gastos)


@given(_lista_gastos_st, _categoria_valida_st)
@settings(max_examples=200)
def test_prop_total_categoria_consistente_con_filtrar(gastos, categoria):
    """
    **Validates: Requirements 2.1, 3.1**

    P3 – Propiedad de partición:
    Para cada categoría presente en total_por_categoria, el total coincide con
    la suma de las cantidades de los gastos devueltos por filtrar_por_categoria.
    """
    totales = total_por_categoria(gastos)
    filtrados = filtrar_por_categoria(gastos, categoria)
    suma_filtrados = round(sum(g["cantidad"] for g in filtrados), 2)

    if categoria in totales:
        assert totales[categoria] == suma_filtrados
    else:
        # Categoría ausente del resultado implica que no hay gastos de esa categoría
        assert suma_filtrados == 0.0


@given(_lista_gastos_st)
@settings(max_examples=200)
def test_prop_ordenar_mismo_contenido(gastos):
    """
    **Validates: Requirements 4.1, 4.2**

    P4 – Invariante de contenido:
    La lista ordenada contiene exactamente los mismos elementos (como multiconjunto
    de cantidades) que la lista original.
    """
    resultado = ordenar_por_importe(gastos)
    assert len(resultado) == len(gastos)
    assert sorted(g["cantidad"] for g in resultado) == sorted(g["cantidad"] for g in gastos)


@given(_lista_gastos_st)
@settings(max_examples=200)
def test_prop_ordenar_no_muta_original(gastos):
    """
    **Validates: Requirements 4.3**

    P5 – Inmutabilidad:
    Invocar ordenar_por_importe no modifica la lista original.
    """
    copia_antes = copy.deepcopy(gastos)
    ordenar_por_importe(gastos)
    assert gastos == copia_antes


@given(_lista_gastos_st, _categoria_valida_st)
@settings(max_examples=200)
def test_prop_filtrar_idempotente(gastos, categoria):
    """
    **Validates: Requirements 3.1, 3.4**

    P6 – Idempotencia:
    Filtrar dos veces produce el mismo resultado que filtrar una sola vez.
    """
    una_vez = filtrar_por_categoria(gastos, categoria)
    dos_veces = filtrar_por_categoria(una_vez, categoria)
    assert una_vez == dos_veces
