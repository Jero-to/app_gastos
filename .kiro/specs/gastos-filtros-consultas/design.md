# Documento de Diseño

## Feature: gastos-filtros-consultas

---

## Visión general

La feature añade un módulo `filtros.py` con cuatro funciones puras de consulta y filtrado, e integra esas funciones en el menú de `gastos.py`. La arquitectura sigue el principio de separación de responsabilidades: `filtros.py` contiene exclusivamente lógica de dominio sin efectos secundarios, y `gastos.py` gestiona la interacción con el usuario y el acceso a ficheros.

---

## Arquitectura de componentes

```
gastos.py  (menú, I/O, persistencia)
    │
    ├── importa ──► filtros.py  (lógica pura de consulta)
    │
    └── lee/escribe ──► gastos.json  (persistencia)
```

### filtros.py

Módulo nuevo. Expone cuatro funciones públicas. No importa `json`, no llama a `input()` ni a `print()`, no accede al sistema de ficheros.

### gastos.py

Módulo existente. Se añaden opciones al menú y se corrige el punto de entrada. No se modifica la lógica de añadir, listar ni eliminar gastos.

---

## Diseño detallado: filtros.py

### Constantes

```python
CATEGORIAS_VALIDAS = {"Alimentacion", "Transporte", "Ocio", "Salud", "Otros"}
```

### Función `total_mensual`

```python
def total_mensual(gastos: list[dict], anio: int, mes: int) -> float:
    """
    Devuelve la suma de las cantidades de los gastos del año y mes dados,
    redondeada a 2 decimales. Devuelve 0.0 si no hay gastos en ese período.

    Args:
        gastos: Lista de dicts con keys 'descripcion', 'cantidad', 'categoria', 'fecha'.
        anio:   Año de 4 dígitos (ej. 2026).
        mes:    Mes entre 1 y 12.

    Returns:
        float redondeado a 2 decimales.

    Precondición: mes in range(1, 13). La validación la hace el llamador (Menu).
    """
    total = sum(
        g["cantidad"]
        for g in gastos
        if _misma_fecha(g["fecha"], anio, mes)
    )
    return round(total, 2)
```

Función auxiliar privada:

```python
def _misma_fecha(fecha_str: str, anio: int, mes: int) -> bool:
    """Comprueba si la cadena 'AAAA-MM-DD' corresponde al año y mes dados."""
    try:
        partes = fecha_str.split("-")
        return int(partes[0]) == anio and int(partes[1]) == mes
    except (IndexError, ValueError):
        return False
```

### Función `total_por_categoria`

```python
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

    Precondición: si mes no es None, mes in range(1, 13).
    """
    filtrados = gastos
    if anio is not None and mes is not None:
        filtrados = [g for g in gastos if _misma_fecha(g["fecha"], anio, mes)]

    resultado: dict[str, float] = {}
    for g in filtrados:
        cat = g["categoria"]
        resultado[cat] = resultado.get(cat, 0.0) + g["cantidad"]

    return {cat: round(total, 2) for cat, total in resultado.items()}
```

### Función `filtrar_por_categoria`

```python
def filtrar_por_categoria(gastos: list[dict], categoria: str) -> list[dict]:
    """
    Devuelve una nueva lista con los gastos cuya categoría coincide exactamente
    con el valor proporcionado. Preserva el orden original.

    Precondición: categoria in CATEGORIAS_VALIDAS. La validación la hace el llamador.
    """
    return [g for g in gastos if g["categoria"] == categoria]
```

### Función `ordenar_por_importe`

```python
def ordenar_por_importe(gastos: list[dict], ascendente: bool = False) -> list[dict]:
    """
    Devuelve una nueva lista de gastos ordenada por cantidad.
    Por defecto orden descendente (mayor a menor).
    No modifica la lista original.

    Args:
        gastos:     Lista original de gastos.
        ascendente: Si True, ordena de menor a mayor.

    Returns:
        Nueva lista ordenada.
    """
    return sorted(gastos, key=lambda g: g["cantidad"], reverse=not ascendente)
```

---

## Diseño detallado: cambios en gastos.py

### Punto de entrada

Sustituir la llamada directa `main()` al final del fichero por:

```python
if __name__ == "__main__":
    main()
```

### Menú ampliado

El menú presenta las nuevas opciones tras las existentes y antes de "Salir". Ejemplo de estructura (los números exactos dependen del menú actual):

```
1. Añadir gasto          ← existente, sin cambios
2. Listar gastos         ← existente, sin cambios
3. Eliminar gasto        ← existente, sin cambios
4. Total mensual         ← nuevo
5. Total por categoría   ← nuevo
6. Filtrar por categoría ← nuevo
7. Ordenar por importe   ← nuevo
8. Salir                 ← siempre la última opción
```

### Integración de las nuevas opciones

Cada nueva opción sigue el patrón:

1. Solicitar parámetros con `input()`.
2. Validar la entrada; si es inválida, imprimir el mensaje de error correspondiente y volver al bucle.
3. Cargar la Lista_Gastos desde `gastos.json` (reutilizando la función de carga ya existente).
4. Invocar la función de `filtros.py`.
5. Mostrar el resultado por consola.

#### Validaciones en gastos.py (no en filtros.py)

| Entrada         | Condición inválida          | Mensaje de error                                                                                              |
|-----------------|-----------------------------|---------------------------------------------------------------------------------------------------------------|
| mes             | No convertible a int        | `"Error: se esperaba un número entero."`                                                                       |
| mes             | int fuera de 1–12           | `"Error: el mes debe ser un número entero entre 1 y 12."`                                                      |
| año             | No convertible a int        | `"Error: se esperaba un número entero."`                                                                       |
| categoría       | No en CATEGORIAS_VALIDAS    | `"Error: categoría no válida. Las categorías válidas son: Alimentacion, Transporte, Ocio, Salud, Otros."`      |

---

## Propiedades de corrección

Las siguientes propiedades son verificables mediante tests de propiedad (property-based testing con `hypothesis`):

### P1 – Invariante de suma: `total_mensual`
Para cualquier Lista_Gastos y cualquier mes válido, `total_mensual` es igual a la suma manual de los gastos filtrados por ese mes, redondeada a 2 decimales.

### P2 – Invariante de tamaño: `filtrar_por_categoria`
Para cualquier Lista_Gastos y Categoria_Valida `c`, el número de elementos en el resultado es menor o igual que la longitud de la lista original.

### P3 – Propiedad de partición: `total_por_categoria` vs `filtrar_por_categoria`
Para cualquier Categoria_Valida `c` presente en el resultado de `total_por_categoria`, el valor `resultado[c]` es igual a `round(sum(g["cantidad"] for g in filtrar_por_categoria(gastos, c)), 2)`.

### P4 – Invariante de contenido: `ordenar_por_importe`
Para cualquier Lista_Gastos, la lista devuelta por `ordenar_por_importe` contiene exactamente los mismos elementos que la original (misma longitud, misma colección de cantidades como multiconjunto).

### P5 – Inmutabilidad: `ordenar_por_importe`
Para cualquier Lista_Gastos, tras invocar `ordenar_por_importe(gastos)`, la Lista_Gastos original permanece sin cambios.

### P6 – Idempotencia: `filtrar_por_categoria`
Para cualquier Lista_Gastos y Categoria_Valida `c`: `filtrar_por_categoria(filtrar_por_categoria(gastos, c), c)` produce el mismo resultado que `filtrar_por_categoria(gastos, c)`.

---

## Estructura de ficheros resultante

```
app_gastos/
├── gastos.py          ← modificado (menú + if __name__)
├── filtros.py         ← nuevo
├── gastos.json        ← sin cambios
└── tests/
    └── test_filtros.py  ← nuevo
```

---

## Decisiones de diseño

| Decisión | Alternativa descartada | Justificación |
|---|---|---|
| Funciones puras en módulo separado | Métodos de clase / lógica incrustada en `main()` | Facilita el testing unitario y el mantenimiento sin tocar la capa de I/O |
| Validación de entradas exclusivamente en `gastos.py` | Lanzar excepciones desde `filtros.py` | Mantiene las funciones puras libres de lógica de presentación; el módulo es reutilizable |
| `sorted()` en lugar de `.sort()` | `.sort()` in-place | Garantiza inmutabilidad de la lista original sin necesidad de copias explícitas |
| Omitir categorías con total 0 en `total_por_categoria` | Incluir siempre las cinco categorías | Resultado más limpio; el llamador puede detectar fácilmente categorías sin gastos por ausencia de clave |
