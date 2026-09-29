"""
gastos.py – Aplicación de registro de gastos por consola.

Gestiona la persistencia en gastos.json e invoca las funciones puras
de consulta y filtrado definidas en filtros.py.
"""
from __future__ import annotations

import json
import os

import filtros

FICHERO = "gastos.json"
CATEGORIAS = ["Alimentacion", "Transporte", "Ocio", "Salud", "Otros"]


# ---------------------------------------------------------------------------
# Helpers de persistencia
# ---------------------------------------------------------------------------

def cargar_gastos() -> list[dict]:
    """Carga y devuelve la lista de gastos desde gastos.json."""
    if not os.path.exists(FICHERO):
        return []
    with open(FICHERO, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_gastos(gastos: list[dict]) -> None:
    """Persiste la lista de gastos en gastos.json."""
    with open(FICHERO, "w", encoding="utf-8") as f:
        json.dump(gastos, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Helpers de presentación
# ---------------------------------------------------------------------------

def mostrar_gastos(gastos: list[dict]) -> None:
    """Imprime la lista de gastos con formato numerado."""
    for i, g in enumerate(gastos, start=1):
        print(f"  {i}. [{g['fecha']}] {g['descripcion']} — {g['cantidad']:.2f} € ({g['categoria']})")


def seleccionar_categoria() -> str | None:
    """
    Muestra el menú de categorías y devuelve la seleccionada,
    o None si la selección es inválida.
    """
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
# Función principal
# ---------------------------------------------------------------------------

def main() -> None:
    """Bucle principal del menú de la aplicación."""
    while True:
        # Cargar gastos al inicio de cada iteración para reflejar cambios
        l2 = cargar_gastos()

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

        # ------------------------------------------------------------------
        # Opción 1: Añadir gasto
        # ------------------------------------------------------------------
        if opcion == "1":
            descripcion = input("Descripción: ").strip()
            cantidad_str = input("Cantidad (€): ").strip()
            try:
                cantidad = float(cantidad_str)
            except ValueError:
                print("Error: se esperaba un número.")
                continue

            cat = seleccionar_categoria()
            if cat is None:
                print("Error: categoría no válida. Las categorías válidas son: Alimentacion, Transporte, Ocio, Salud, Otros.")
                continue

            fecha = input("Fecha (AAAA-MM-DD): ").strip()

            nuevo_gasto = {
                "descripcion": descripcion,
                "cantidad": cantidad,
                "categoria": cat,
                "fecha": fecha,
            }
            l2.append(nuevo_gasto)
            guardar_gastos(l2)
            print("Gasto añadido correctamente.")

        # ------------------------------------------------------------------
        # Opción 2: Listar gastos
        # ------------------------------------------------------------------
        elif opcion == "2":
            if not l2:
                print("No hay gastos registrados.")
            else:
                print(f"\n--- Gastos ({len(l2)} en total) ---")
                mostrar_gastos(l2)

        # ------------------------------------------------------------------
        # Opción 3: Eliminar gasto
        # ------------------------------------------------------------------
        elif opcion == "3":
            if not l2:
                print("No hay gastos registrados.")
                continue
            print(f"\n--- Gastos ({len(l2)} en total) ---")
            mostrar_gastos(l2)
            num_str = input("Número del gasto a eliminar: ").strip()
            try:
                num = int(num_str)
            except ValueError:
                print("Error: se esperaba un número entero.")
                continue
            if num < 1 or num > len(l2):
                print(f"Error: número fuera de rango (1-{len(l2)}).")
                continue
            eliminado = l2.pop(num - 1)
            guardar_gastos(l2)
            print(f"Gasto eliminado: {eliminado['descripcion']} — {eliminado['cantidad']:.2f} €")

        # ------------------------------------------------------------------
        # Opción 4: Total mensual
        # ------------------------------------------------------------------
        elif opcion == "4":
            anio_str = input("Año: ").strip()
            mes_str = input("Mes (1-12): ").strip()
            try:
                anio = int(anio_str)
            except ValueError:
                print("Error: se esperaba un número entero.")
                continue
            try:
                mes = int(mes_str)
            except ValueError:
                print("Error: se esperaba un número entero.")
                continue
            if mes < 1 or mes > 12:
                print("Error: el mes debe ser un número entero entre 1 y 12.")
                continue
            total = filtros.total_mensual(l2, anio, mes)
            print(f"Total en {mes:02d}/{anio}: {total:.2f} €")

        # ------------------------------------------------------------------
        # Opción 5: Total por categoría
        # ------------------------------------------------------------------
        elif opcion == "5":
            filtrar_mes = input("¿Filtrar por mes? (s/n): ").strip().lower()
            if filtrar_mes == "s":
                anio_str = input("Año: ").strip()
                mes_str = input("Mes (1-12): ").strip()
                try:
                    anio = int(anio_str)
                except ValueError:
                    print("Error: se esperaba un número entero.")
                    continue
                try:
                    mes = int(mes_str)
                except ValueError:
                    print("Error: se esperaba un número entero.")
                    continue
                if mes < 1 or mes > 12:
                    print("Error: el mes debe ser un número entero entre 1 y 12.")
                    continue
                resultado = filtros.total_por_categoria(l2, anio, mes)
            else:
                resultado = filtros.total_por_categoria(l2)

            if not resultado:
                print("No hay gastos registrados.")
            else:
                print("\n--- Total por categoría ---")
                for cat, total in resultado.items():
                    print(f"  {cat}: {total:.2f} €")

        # ------------------------------------------------------------------
        # Opción 6: Filtrar por categoría
        # ------------------------------------------------------------------
        elif opcion == "6":
            cat = seleccionar_categoria()
            if cat is None:
                print("Error: categoría no válida. Las categorías válidas son: Alimentacion, Transporte, Ocio, Salud, Otros.")
                continue
            resultado = filtros.filtrar_por_categoria(l2, cat)
            if not resultado:
                print("No hay gastos en esa categoría.")
            else:
                print(f"\n--- Gastos en '{cat}' ({len(resultado)}) ---")
                mostrar_gastos(resultado)

        # ------------------------------------------------------------------
        # Opción 7: Ordenar por importe
        # ------------------------------------------------------------------
        elif opcion == "7":
            orden_str = input("¿Orden ascendente? (s/n): ").strip().lower()
            ascendente = orden_str == "s"
            resultado = filtros.ordenar_por_importe(l2, ascendente)
            if not resultado:
                print("No hay gastos registrados.")
            else:
                direccion = "ascendente" if ascendente else "descendente"
                print(f"\n--- Gastos ordenados por importe ({direccion}) ---")
                mostrar_gastos(resultado)

        # ------------------------------------------------------------------
        # Opción 8: Salir
        # ------------------------------------------------------------------
        elif opcion == "8":
            print("¡Hasta luego!")
            break

        # ------------------------------------------------------------------
        # Opción no válida
        # ------------------------------------------------------------------
        else:
            print("Opción no válida. Elige entre 1 y 8.")


if __name__ == "__main__":
    main()
