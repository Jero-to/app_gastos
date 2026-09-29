"""
tests/test_filtros.py

Tests unitarios (ejemplo-based) y de propiedad (hypothesis) para filtros.py.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import copy
import pytest
from hypothesis import given, settings
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
# Fixture compartida
# ---------------------------------------------------------------------------

@pytest.fixture
def gastos():
    return [
        {"descripcion": "Supermercado", "cantidad": 50.25, "categoria": "Alimentación", "fecha": "2026-09-03"},
        {"descripcion": "Metro",        "cantidad": 12.50, "categoria": "Transporte",   "fecha": "2026-09-10"},
        {"descripcion": "Cine",         "cantidad": 30.00, "categoria": "Ocio",         "fecha": "2026-09-15"},
        {"descripcion": "Fruta",        "cantidad": 20.10, "categoria": "Alimentación", "fecha": "2026-10-01"},
        {"descripcion": "Dentista",     "cantidad": 45.00, "categoria": "Salud",        "fecha": "2025-09-20"},
    ]


# ---------------------------------------------------------------------------
# total_mensual
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "anio, mes, esperado",
    [
        (2026, 9,  92.75),   # Supermercado + Metro + Cine
        (2026, 10, 20.10),   # solo Fruta
        (2025, 9,  45.00),   # mismo mes, distinto año
        (2026, 1,  0),       # mes sin gastos
    ],
)
def test_total_mensual(gastos, anio, mes, esperado):
    assert total_mensual(gastos, anio, mes) == pytest.approx(esperado)


def test_total_mensual_lista_vacia():
    assert total_mensual([], 2026, 9) == 0


# ---------------------------------------------------------------------------
# total_por_categoria
# ---------------------------------------------------------------------------

def test_total_por_categoria_global(gastos):
    res = total_por_categoria(gastos)
    assert res.get("Alimentación", 0) == pytest.approx(70.35)
    assert res.get("Transporte",   0) == pytest.approx(12.50)
    assert res.get("Ocio",         0) == pytest.approx(30.00)
    assert res.get("Salud",        0) == pytest.approx(45.00)


def test_total_por_categoria_de_un_mes(gastos):
    res = total_por_categoria(gastos, 2026, 9)
    assert res.get("Alimentación", 0) == pytest.approx(50.25)
    assert res.get("Salud",        0) == 0


def test_total_por_categoria_lista_vacia():
    res = total_por_categoria([])
    assert sum(res.values()) == 0


# ---------------------------------------------------------------------------
# filtrar_por_categoria
# ---------------------------------------------------------------------------

def test_filtrar_por_categoria(gastos):
    res = filtrar_por_categoria(gastos, "Alimentación")
    assert len(res) == 2
    assert all(g["categoria"] == "Alimentación" for g in res)


def test_filtrar_por_categoria_sin_resultados(gastos):
    assert filtrar_por_categoria(gastos, "Viajes") == []


def test_filtrar_lista_vacia():
    assert filtrar_por_categoria([], "Ocio") == []


# ---------------------------------------------------------------------------
# ordenar_por_importe
# ---------------------------------------------------------------------------

def test_ordenar_descendente_por_defecto(gastos):
    res = ordenar_por_importe(gastos)
    assert [g["cantidad"] for g in res] == [50.25, 45.00, 30.00, 20.10, 12.50]


def test_ordenar_no_modifica_la_lista_original(gastos):
    copia = list(gastos)
    ordenar_por_importe(gastos)
    assert gastos == copia


def test_ordenar_lista_vacia():
    assert ordenar_por_importe([]) == []


# ---------------------------------------------------------------------------
# Tests de propiedad (hypothesis)
# ---------------------------------------------------------------------------

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

_lista_gastos_st    = st.lists(_gasto_st, min_size=0, max_size=20)
_categoria_valida_st = st.sampled_from(sorted(CATEGORIAS_VALIDAS))
_anio_st            = st.integers(min_value=2000, max_value=2100)
_mes_st             = st.integers(min_value=1,    max_value=12)


@given(_lista_gastos_st, _anio_st, _mes_st)
@settings(max_examples=200)
def test_prop_total_mensual_igual_suma_manual(gastos_prop, anio, mes):
    """P1 – Invariante de suma."""
    esperado = round(
        sum(g["cantidad"] for g in gastos_prop if filtros._misma_fecha(g["fecha"], anio, mes)),
        2,
    )
    assert total_mensual(gastos_prop, anio, mes) == esperado


@given(_lista_gastos_st, _categoria_valida_st)
@settings(max_examples=200)
def test_prop_filtrar_tamano_menor_o_igual(gastos_prop, categoria):
    """P2 – Invariante de tamaño."""
    assert len(filtrar_por_categoria(gastos_prop, categoria)) <= len(gastos_prop)


@given(_lista_gastos_st, _categoria_valida_st)
@settings(max_examples=200)
def test_prop_total_categoria_consistente_con_filtrar(gastos_prop, categoria):
    """P3 – Propiedad de partición."""
    totales   = total_por_categoria(gastos_prop)
    filtrados = filtrar_por_categoria(gastos_prop, categoria)
    suma_filtrados = round(sum(g["cantidad"] for g in filtrados), 2)
    if categoria in totales:
        assert totales[categoria] == suma_filtrados
    else:
        assert suma_filtrados == 0.0


@given(_lista_gastos_st)
@settings(max_examples=200)
def test_prop_ordenar_mismo_contenido(gastos_prop):
    """P4 – Invariante de contenido."""
    resultado = ordenar_por_importe(gastos_prop)
    assert len(resultado) == len(gastos_prop)
    assert sorted(g["cantidad"] for g in resultado) == sorted(g["cantidad"] for g in gastos_prop)


@given(_lista_gastos_st)
@settings(max_examples=200)
def test_prop_ordenar_no_muta_original(gastos_prop):
    """P5 – Inmutabilidad."""
    copia_antes = copy.deepcopy(gastos_prop)
    ordenar_por_importe(gastos_prop)
    assert gastos_prop == copia_antes


@given(_lista_gastos_st, _categoria_valida_st)
@settings(max_examples=200)
def test_prop_filtrar_idempotente(gastos_prop, categoria):
    """P6 – Idempotencia."""
    una_vez  = filtrar_por_categoria(gastos_prop, categoria)
    dos_veces = filtrar_por_categoria(una_vez, categoria)
    assert una_vez == dos_veces
