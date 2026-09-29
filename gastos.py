"""gastos.py – Aplicación de registro de gastos por consola."""
from __future__ import annotations

import json
import os
from datetime import datetime

import filtros

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

FICHERO: str = "gastos.json"
FECHA_FMT: str = "%Y-%m-%d"
CATEGORIAS: list[str] = ["Alimentacion", "Transporte", "Ocio", "Salud", "Otros"]

MSG_CAT_INVALIDA: str = (
    "Error: categoría no válida. Las categorías válidas son: "
    "Alimentacion, Transporte, Ocio, Salud, Otros."
)

# ---------------------------------------------------------------------------
# Persistencia
# ---------------------------------------------------------------------------

def cargar_gastos() -> list[dict]:
    """Devuelve la lista de gastos desde FICHERO, o [] si no existe."""
    if not os.path.exists(FICHERO):
        return []
    with open(FICHERO, "r", encoding="utf-8") as fh:
        return json.load(fh)


def guardar_gastos(gastos: list[dict]) -> None:
    """Persiste la lista de gastos en FICHERO."""
    with open(FICHERO, "w", encoding="utf-8") as fh:
        json.dump(gastos, fh, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Presentación
# ---------------------------------------------------------------------------

def mostrar_gastos(gastos: list[dict]) -> None:
    """Imprime cada gasto numerado con formato estándar."""
    for i, gasto in enumerate(gastos, start=1):
        print(f"  {i}. [{gasto['fecha']}] {gasto['descripcion']} — {gasto['cantidad']:.2f} € ({gasto['categoria']})")


def seleccionar_categoria() -> str | None:
    """Muestra el menú de categorías y devuelve la elegida, o None si es inválida."""
    print("  Categorías:")
    for i, cat in enumerate(CATEGORIAS, start=1):
        print(f"    {i}. {cat}")
    seleccion = input("Selecciona categoría (1-5): ").strip()
    try:
        idx = int(seleccion) - 1
        if 0 <= idx < len(CATEGORIAS):
            return CATEGORIAS[idx]
    except ValueError:
        pass
    return None


# ---------------------------------------------------------------------------
# Entrada validada compartida
# ---------------------------------------------------------------------------

def _pedir_anio_mes() -> tuple[int, int] | None:
    """Pide año y mes, valida rango y devuelve (anio, mes) o None si hay error."""
    anio_str = input("Año: ").strip()
    mes_str = input("Mes (1-12): ").strip()
    try:
        anio = int(anio_str)
    except ValueError:
        print("Error: se esperaba un número entero.")
        return None
    try:
        mes = int(mes_str)
    except ValueError:
        print("Error: se esperaba un número entero.")
        return None
    if not 1 <= mes <= 12:
        print("Error: el mes debe ser un número entero entre 1 y 12.")
        return None
    return anio, mes


# ---------------------------------------------------------------------------
# Acciones del menú
# ---------------------------------------------------------------------------

def _aniadir(gastos: list[dict]) -> None:
    """Pide datos al usuario y añade un nuevo gasto."""
    descripcion = input("Descripción: ").strip()
    cantidad_str = input("Cantidad (€): ").strip()
    try:
        cantidad = float(cantidad_str)
    except ValueError:
        print("Error: se esperaba un número.")
        return

    categoria = seleccionar_categoria()
    if categoria is None:
        print(MSG_CAT_INVALIDA)
        return

    fecha_str = input("Fecha (AAAA-MM-DD): ").strip()
    try:
        datetime.strptime(fecha_str, FECHA_FMT)
    except ValueError:
        print("Error: formato de fecha incorrecto. Use AAAA-MM-DD.")
        return

    gastos.append({
        "descripcion": descripcion,
        "cantidad": cantidad,
        "categoria": categoria,
        "fecha": fecha_str,
    })
    guardar_gastos(gastos)
    print("Gasto añadido correctamente.")


def _listar(gastos: list[dict]) -> None:
    """Muestra todos los gastos o avisa si no hay ninguno."""
    if not gastos:
        print("No hay gastos registrados.")
        return
    print(f"\n--- Gastos ({len(gastos)} en total) ---")
    mostrar_gastos(gastos)


def _eliminar(gastos: list[dict]) -> None:
    """Elimina el gasto indicado por el usuario."""
    if not gastos:
        print("No hay gastos registrados.")
        return
    print(f"\n--- Gastos ({len(gastos)} en total) ---")
    mostrar_gastos(gastos)
    num_str = input("Número del gasto a eliminar: ").strip()
    try:
        num = int(num_str)
    except ValueError:
        print("Error: se esperaba un número entero.")
        return
    if not 1 <= num <= len(gastos):
        print(f"Error: número fuera de rango (1-{len(gastos)}).")
        return
    eliminado = gastos.pop(num - 1)
    guardar_gastos(gastos)
    print(f"Gasto eliminado: {eliminado['descripcion']} — {eliminado['cantidad']:.2f} €")


def _total_mensual(gastos: list[dict]) -> None:
    """Muestra el total gastado en el mes y año indicados."""
    periodo = _pedir_anio_mes()
    if periodo is None:
        return
    anio, mes = periodo
    total = filtros.total_mensual(gastos, anio, mes)
    print(f"Total en {mes:02d}/{anio}: {total:.2f} €")


def _total_por_categoria(gastos: list[dict]) -> None:
    """Muestra el total por categoría, con filtro opcional de mes."""
    filtrar_mes = input("¿Filtrar por mes? (s/n): ").strip().lower()
    if filtrar_mes == "s":
        periodo = _pedir_anio_mes()
        if periodo is None:
            return
        anio, mes = periodo
        totales = filtros.total_por_categoria(gastos, anio, mes)
    else:
        totales = filtros.total_por_categoria(gastos)

    if not totales:
        print("No hay gastos registrados.")
        return
    print("\n--- Total por categoría ---")
    for cat, total in totales.items():
        print(f"  {cat}: {total:.2f} €")


def _filtrar_por_categoria(gastos: list[dict]) -> None:
    """Muestra los gastos de una categoría elegida por el usuario."""
    categoria = seleccionar_categoria()
    if categoria is None:
        print(MSG_CAT_INVALIDA)
        return
    resultado = filtros.filtrar_por_categoria(gastos, categoria)
    if not resultado:
        print("No hay gastos en esa categoría.")
        return
    print(f"\n--- Gastos en '{categoria}' ({len(resultado)}) ---")
    mostrar_gastos(resultado)


def _ordenar_por_importe(gastos: list[dict]) -> None:
    """Muestra los gastos ordenados por importe."""
    orden_str = input("¿Orden ascendente? (s/n): ").strip().lower()
    ascendente = orden_str == "s"
    resultado = filtros.ordenar_por_importe(gastos, ascendente)
    if not resultado:
        print("No hay gastos registrados.")
        return
    direccion = "ascendente" if ascendente else "descendente"
    print(f"\n--- Gastos ordenados por importe ({direccion}) ---")
    mostrar_gastos(resultado)


# ---------------------------------------------------------------------------
# Despacho de opciones
# ---------------------------------------------------------------------------

_OPCIONES: dict[str, object] = {
    "1": _aniadir,
    "2": _listar,
    "3": _eliminar,
    "4": _total_mensual,
    "5": _total_por_categoria,
    "6": _filtrar_por_categoria,
    "7": _ordenar_por_importe,
}


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

def main() -> None:
    """Bucle principal: muestra el menú y despacha cada opción."""
    while True:
        gastos = cargar_gastos()

        print("\n=== Menú de gastos ===")
        print("  1. Añadir gasto")
        print("  2. Listar gastos")
        print("  3. Eliminar gasto")
        print("  4. Total mensual")
        print("  5. Total por categoría")
        print("  6. Filtrar por categoría")
        print("  7. Ordenar por importe")
        print("  8. Salir")
        opcion = input("Elige una opción: ").strip()

        if opcion == "8":
            print("¡Hasta luego!")
            break

        accion = _OPCIONES.get(opcion)
        if accion is None:
            print("Opción no válida. Elige entre 1 y 8.")
            continue

        accion(gastos)


if __name__ == "__main__":
    main()
