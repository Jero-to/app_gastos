"""
filtros.py – Módulo de consulta y filtrado de gastos.

Expone funciones puras: sin llamadas a input(), print() ni acceso a ficheros.
Toda la validación de entradas (mes fuera de rango, categoría inválida, etc.)
es responsabilidad del llamador (gastos.py).
"""
from __future__ import annotations

CATEGORIAS_VALIDAS = {"Alimentacion", "Transporte", "Ocio", "Salud", "Otros"}


# ---------------------------------------------------------------------------
# Funciones auxiliares privadas
# ---------------------------------------------------------------------------

def _misma_fecha(fecha_str: str, anio: int, mes: int) -> bool:
    """Devuelve True si la cadena 'AAAA-MM-DD' corresponde al año y mes dados."""
    try:
        partes = fecha_str.split("-")
        return int(partes[0]) == anio and int(partes[1]) == mes
    except (IndexError, ValueError):
        return False


# ---------------------------------------------------------------------------
# Funciones públicas
# ---------------------------------------------------------------------------

def total_mensual(gastos: list[dict], anio: int, mes: int) -> float:
    """
    Devuelve la suma de las cantidades de los gastos del año y mes dados,
    redondeada a 2 decimales. Devuelve 0.0 si no hay gastos en ese período.

    Args:
        gastos: Lista de dicts con keys 'descripcion', 'cantidad', 'categoria', 'fecha'.
        anio:   Año de 4 dígitos (ej. 2026).
        mes:    Mes entre 1 y 12 (la validación la realiza el llamador).

    Returns:
        float redondeado a 2 decimales.
    """
    total = sum(
        g["cantidad"]
        for g in gastos
        if _misma_fecha(g["fecha"], anio, mes)
    )
    return round(total, 2)


def total_por_categoria(
    gastos: list[dict],
    anio: int | None = None,
    mes: int | None = None,
) -> dict[str, float]:
    """
    Devuelve un dict {categoria: total} con los gastos agrupados por categoría.
    Si se pasan anio y mes, restringe al período indicado.
    Solo incluye categorías con al menos un gasto (sin entradas con valor 0.0).
    Cada total está redondeado a 2 decimales.

    Args:
        gastos: Lista de dicts de gastos.
        anio:   Año de 4 dígitos; si es None no se filtra por período.
        mes:    Mes entre 1 y 12; si es None no se filtra por período.
                La validación de rango la realiza el llamador.

    Returns:
        dict[str, float] con los totales por categoría.
    """
    filtrados = gastos
    if anio is not None and mes is not None:
        filtrados = [g for g in gastos if _misma_fecha(g["fecha"], anio, mes)]

    resultado: dict[str, float] = {}
    for g in filtrados:
        cat = g["categoria"]
        resultado[cat] = resultado.get(cat, 0.0) + g["cantidad"]

    return {cat: round(total, 2) for cat, total in resultado.items()}


def filtrar_por_categoria(gastos: list[dict], categoria: str) -> list[dict]:
    """
    Devuelve una nueva lista con los gastos cuya categoría coincide exactamente
    con el valor proporcionado. Preserva el orden original.

    Args:
        gastos:    Lista de dicts de gastos.
        categoria: Valor de categoría a filtrar (la validación la realiza el llamador).

    Returns:
        Nueva lista de dicts de gastos filtrada.
    """
    return [g for g in gastos if g["categoria"] == categoria]


def ordenar_por_importe(gastos: list[dict], ascendente: bool = False) -> list[dict]:
    """
    Devuelve una nueva lista de gastos ordenada por cantidad.
    Por defecto orden descendente (mayor a menor).
    No modifica la lista original.

    Args:
        gastos:     Lista original de gastos.
        ascendente: Si True, ordena de menor a mayor; si False (por defecto),
                    ordena de mayor a menor.

    Returns:
        Nueva lista ordenada sin modificar la original.
    """
    return sorted(gastos, key=lambda g: g["cantidad"], reverse=not ascendente)
