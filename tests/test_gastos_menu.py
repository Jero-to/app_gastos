"""
tests/test_gastos_menu.py

Tests de no-regresión para las opciones originales del menú de gastos.py:
añadir gasto (opción 1), listar gastos (opción 2) y eliminar gasto (opción 3).

Estrategia de aislamiento:
  - gastos.FICHERO se parchea con monkeypatch para apuntar a un fichero
    temporal bajo tmp_path; el gastos.json real nunca se toca.
  - builtins.input se parchea con unittest.mock.patch para inyectar una
    secuencia predefinida de respuestas sin interacción de consola.
  - La salida estándar se captura con el fixture capsys de pytest.
"""
import sys
import os

# Asegura que pytest encuentre gastos.py desde este directorio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
from unittest.mock import patch

import gastos
from gastos import main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _patch_fichero(monkeypatch, tmp_path):
    """Apunta gastos.FICHERO a un fichero temporal vacío."""
    fichero_tmp = str(tmp_path / "gastos_test.json")
    monkeypatch.setattr(gastos, "FICHERO", fichero_tmp)
    return fichero_tmp


def _leer_gastos(fichero: str) -> list:
    """Lee y devuelve la lista de gastos del fichero JSON dado."""
    if not os.path.exists(fichero):
        return []
    with open(fichero, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_listar_sin_gastos(tmp_path, monkeypatch, capsys):
    """
    Opción 2 (listar gastos) con gastos.json vacío muestra
    'No hay gastos registrados.'
    """
    fichero_tmp = _patch_fichero(monkeypatch, tmp_path)

    # Secuencia: opción 2 → listar, opción 8 → salir
    inputs = iter(["2", "8"])
    with patch("builtins.input", side_effect=inputs):
        main()

    salida = capsys.readouterr().out
    assert "No hay gastos registrados." in salida


def test_aniadir_gasto(tmp_path, monkeypatch, capsys):
    """
    Opción 1 (añadir gasto) con entradas válidas persiste el gasto
    en gastos.json correctamente.
    """
    fichero_tmp = _patch_fichero(monkeypatch, tmp_path)

    # Secuencia: opción 1 → descripción, cantidad, categoría (2=Transporte),
    # fecha, opción 8 → salir
    inputs = iter(["1", "Taxi aeropuerto", "25.50", "2", "2024-03-15", "8"])
    with patch("builtins.input", side_effect=inputs):
        main()

    gastos_guardados = _leer_gastos(fichero_tmp)
    assert len(gastos_guardados) == 1
    gasto = gastos_guardados[0]
    assert gasto["descripcion"] == "Taxi aeropuerto"
    assert gasto["cantidad"] == 25.50
    assert gasto["categoria"] == "Transporte"
    assert gasto["fecha"] == "2024-03-15"

    salida = capsys.readouterr().out
    assert "Gasto añadido correctamente." in salida


def test_listar_con_gastos(tmp_path, monkeypatch, capsys):
    """
    Opción 2 (listar gastos) muestra el gasto añadido previamente.
    """
    fichero_tmp = _patch_fichero(monkeypatch, tmp_path)

    # Primero se añade un gasto y luego se lista, finalmente se sale
    inputs = iter([
        "1", "Mercado semanal", "45.00", "1", "2024-04-10",  # añadir (cat 1=Alimentacion)
        "2",                                                   # listar
        "8",                                                   # salir
    ])
    with patch("builtins.input", side_effect=inputs):
        main()

    salida = capsys.readouterr().out
    assert "Mercado semanal" in salida
    assert "45.00" in salida


def test_eliminar_gasto(tmp_path, monkeypatch, capsys):
    """
    Opción 3 (eliminar gasto) con índice "1" elimina el único gasto existente;
    gastos.json queda vacío.
    """
    fichero_tmp = _patch_fichero(monkeypatch, tmp_path)

    # Añadir un gasto, eliminarlo y salir
    inputs = iter([
        "1", "Farmacia", "12.75", "4", "2024-05-20",  # añadir (cat 4=Salud)
        "3", "1",                                       # eliminar nº 1
        "8",                                            # salir
    ])
    with patch("builtins.input", side_effect=inputs):
        main()

    gastos_finales = _leer_gastos(fichero_tmp)
    assert gastos_finales == []

    salida = capsys.readouterr().out
    assert "Gasto eliminado" in salida


def test_opcion_no_valida(tmp_path, monkeypatch, capsys):
    """
    Una opción desconocida muestra 'Opción no válida. Elige entre 1 y 8.'
    """
    _patch_fichero(monkeypatch, tmp_path)

    inputs = iter(["9", "8"])
    with patch("builtins.input", side_effect=inputs):
        main()

    salida = capsys.readouterr().out
    assert "Opción no válida. Elige entre 1 y 8." in salida
