# Plan de refactorización de `gastos.py`

## 1. Constantes con nombre (eliminar números y cadenas mágicas)

```python
# Antes (disperso por todo el fichero)
FICHERO = "gastos.json"
CATEGORIAS = ["Alimentacion", ...]   # ya existía, bien

# Añadir
FECHA_FMT = "%Y-%m-%d"
MSG_CAT_INVALIDA = "Error: categoría no válida. Las categorías válidas son: ..."
```

---

## 2. Extraer funciones pequeñas de `main()`

`main()` tenía ~130 líneas. Se divide así:

| Función nueva | Responsabilidad |
|---|---|
| `seleccionar_categoria()` | Ya existía — sin cambios de comportamiento |
| `_pedir_anio_mes()` | Pide año y mes, valida, devuelve `(anio, mes)` o `None` — elimina duplicación entre opción 4 y opción 5 |
| `_aniadir(gastos)` | Lógica completa de la opción 1 |
| `_listar(gastos)` | Lógica completa de la opción 2 |
| `_eliminar(gastos)` | Lógica completa de la opción 3 |
| `_total_mensual(gastos)` | Lógica completa de la opción 4 |
| `_total_por_categoria(gastos)` | Lógica completa de la opción 5 |
| `_filtrar_por_categoria(gastos)` | Lógica completa de la opción 6 |
| `_ordenar_por_importe(gastos)` | Lógica completa de la opción 7 |

`main()` queda como un bucle de ~20 líneas que despacha con un diccionario:

```python
_OPCIONES = {"1": _aniadir, "2": _listar, ...}
```

---

## 3. Retornos tempranos en lugar de `if` anidados

```python
# Antes — anidado (4 niveles de indentación)
if d == "":
    print("Error...")
else:
    cant = input(...)
    try:
        ...
        if cant <= 0:
            ...
        else:
            # lógica principal enterrada aquí dentro
```

```python
# Después — plano con retornos tempranos
descripcion = input(...).strip()
cantidad_str = input(...).strip()
try:
    cantidad = float(cantidad_str)
except ValueError:
    print("Error: se esperaba un número.")
    return          # retorno temprano, sin else

categoria = seleccionar_categoria()
if categoria is None:
    print(MSG_CAT_INVALIDA)
    return          # retorno temprano, sin else

# lógica principal al nivel raíz de la función
```

---

## 4. Nombres descriptivos

| Antes | Después |
|---|---|
| `l2` | `gastos` |
| `d` | `descripcion` |
| `cant` | `cantidad` |
| `cat` | `categoria` |
| `tmp` | `opcion` |
| `x` | `FICHERO` (constante) |

---

## 5. Validación de fecha con `datetime.strptime`

```python
# Antes — partir la cadena a mano
partes = fecha.split("-")
if len(partes) != 3 or len(partes[0]) != 4 or len(partes[1]) != 2 or len(partes[2]) != 2:
    print("Error: formato de fecha incorrecto.")
else:
    try:
        int(partes[0]); int(partes[1]); int(partes[2])
        ...
    except ValueError:
        print("Error: la fecha contiene caracteres no numéricos.")
```

```python
# Después — una sola llamada estándar
from datetime import datetime

try:
    datetime.strptime(fecha_str, FECHA_FMT)   # FECHA_FMT = "%Y-%m-%d"
except ValueError:
    print("Error: formato de fecha incorrecto. Use AAAA-MM-DD.")
    return
```

---

## 6. `with open(...)`, type hints y docstrings

- `cargar_gastos` y `guardar_gastos` ya usaban `with open` — sin cambios.
- Se añaden **type hints** a todas las funciones: `-> None`, `-> list[dict]`, `-> str | None`, etc.
- Se añade un **docstring de una línea** a cada función describiendo su responsabilidad.

---

## Lo que NO cambia

- Textos exactos del menú y mensajes de error
- Orden y numeración de las opciones (1-8)
- Formato de `gastos.json` (`ensure_ascii=False`, `indent=2`, ruta relativa `"gastos.json"`)
- `filtros.py` y la carpeta `tests/`
- `if __name__ == "__main__": main()` al final del fichero
