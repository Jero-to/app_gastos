import json
import os


def main():
    x = "gastos.json"

    if os.path.exists("gastos.json"):
        f = open("gastos.json", "r")
        l2 = json.load(f)
        f.close()
    else:
        l2 = []

    while True:
        print("")
        print("=== APP DE GASTOS ===")
        print("1. Añadir gasto")
        print("2. Listar gastos")
        print("3. Eliminar gasto")
        print("4. Salir")
        print("")
        tmp = input("Elige una opción: ").strip()

        if tmp == "1":
            print("")
            d = input("Descripción: ").strip()
            if d == "":
                print("Error: la descripción no puede estar vacía.")
            else:
                cant = input("Cantidad (ej: 12.50): ").strip()
                try:
                    cant = float(cant)
                    if cant <= 0:
                        print("Error: la cantidad debe ser mayor que cero.")
                    else:
                        print("")
                        print("Categorías disponibles:")
                        print("  1. Alimentación")
                        print("  2. Transporte")
                        print("  3. Ocio")
                        print("  4. Salud")
                        print("  5. Otros")
                        cat_op = input("Elige categoría (1-5): ").strip()
                        if cat_op == "1":
                            cat = "Alimentación"
                        elif cat_op == "2":
                            cat = "Transporte"
                        elif cat_op == "3":
                            cat = "Ocio"
                        elif cat_op == "4":
                            cat = "Salud"
                        elif cat_op == "5":
                            cat = "Otros"
                        else:
                            cat = None
                        if cat is None:
                            print("Error: categoría no válida.")
                        else:
                            fecha = input("Fecha (AAAA-MM-DD): ").strip()
                            partes = fecha.split("-")
                            if len(partes) != 3 or len(partes[0]) != 4 or len(partes[1]) != 2 or len(partes[2]) != 2:
                                print("Error: formato de fecha incorrecto.")
                            else:
                                try:
                                    int(partes[0])
                                    int(partes[1])
                                    int(partes[2])
                                    gasto = {}
                                    gasto["descripcion"] = d
                                    gasto["cantidad"] = cant
                                    gasto["categoria"] = cat
                                    gasto["fecha"] = fecha
                                    l2.append(gasto)
                                    f = open("gastos.json", "w")
                                    json.dump(l2, f, ensure_ascii=False, indent=2)
                                    f.close()
                                    print("Gasto añadido correctamente.")
                                except ValueError:
                                    print("Error: la fecha contiene caracteres no numéricos.")
                except ValueError:
                    print("Error: la cantidad introducida no es un número válido.")

        elif tmp == "2":
            print("")
            if len(l2) == 0:
                print("No hay gastos registrados.")
            else:
                print(f"{'Nº':<4} {'Fecha':<12} {'Categoría':<15} {'Cantidad':>10}  Descripción")
                print("-" * 60)
                i = 0
                while i < len(l2):
                    g = l2[i]
                    print(f"{i+1:<4} {g['fecha']:<12} {g['categoria']:<15} {g['cantidad']:>10.2f}  {g['descripcion']}")
                    i = i + 1

        elif tmp == "3":
            print("")
            if len(l2) == 0:
                print("No hay gastos registrados.")
            else:
                i = 0
                while i < len(l2):
                    g = l2[i]
                    print(f"{i+1}. [{g['fecha']}] {g['descripcion']} - {g['cantidad']:.2f} € ({g['categoria']})")
                    i = i + 1
                print("")
                num = input("Número del gasto a eliminar: ").strip()
                try:
                    num = int(num)
                    if num < 1 or num > len(l2):
                        print("Error: número fuera de rango.")
                    else:
                        eliminado = l2[num - 1]
                        l2.pop(num - 1)
                        f = open("gastos.json", "w")
                        json.dump(l2, f, ensure_ascii=False, indent=2)
                        f.close()
                        print(f"Gasto '{eliminado['descripcion']}' eliminado correctamente.")
                except ValueError:
                    print("Error: introduce un número válido.")

        elif tmp == "4":
            print("Hasta luego.")
            break

        else:
            print("Opción no válida. Elige entre 1 y 4.")


main()
