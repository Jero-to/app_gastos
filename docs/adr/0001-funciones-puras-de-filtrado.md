---
# ADR 0001 — Funciones puras de filtrado en módulo separado

- **Estado:** Aceptado
- **Fecha:** 2025-07-15
- **Feature:** gastos-filtros-consultas

---

## Contexto

La aplicación de registro de gastos (`gastos.py`) es un script con una única función
`main()` de estilo legacy: todo el flujo —lectura de fichero, validación de entrada,
lógica de negocio y presentación— convive dentro del mismo bucle. Esto funciona para
las operaciones CRUD básicas, pero añadir consultas y filtros (total mensual, total por
categoría, filtrado y ordenación) dentro del mismo `main()` agravaría el problema:
la lógica de dominio quedaría acoplada a `input()`, `print()` y a la ruta concreta de
`gastos.json`, haciendo imposible probarla de forma aislada.

El equipo decidió introducir las nuevas capacidades de consulta antes de añadir tests
automatizados, lo que exigía elegir una organización que hiciera esas funciones
verificables sin arrancar el menú interactivo.

---

## Decisión

Toda la lógica de consulta y filtrado se implementa como **funciones puras** en un
**módulo independiente `filtros.py`**. Las funciones no llaman a `input()` ni a
`print()`, no acceden a ficheros y no modifican sus argumentos. `gastos.py` se limita
a cargar los datos, delegar en `filtros.py` y mostrar el resultado.

---

## Alternativas consideradas

| Alternativa | Pros | Contras | Motivo de descarte |
|---|---|---|---|
| **A. Funciones puras en `filtros.py`** *(decisión adoptada)* | Testeable de forma aislada; reutilizable desde otros contextos; `gastos.py` no crece; separación clara de responsabilidades | Requiere un fichero adicional; el alumno debe gestionar dos módulos | — |
| **B. Funciones dentro de `main()` en `gastos.py`** | Sin ficheros extra; coherente con el estilo legacy existente | Imposible de probar sin mockear `input()`/`print()`/fichero; `main()` supera las 150 líneas y se vuelve inmantenible | Viola el requisito de testabilidad; perpetúa el acoplamiento que ya se consideró un problema |
| **C. Clase `GestorGastos` con métodos de consulta** | Agrupa estado y comportamiento; familiar para desarrolladores OOP | Introduce un patrón de diseño sin beneficio real en un script de consola; complica el testing con instanciación y estado interno | Sobreingeniería para el tamaño del proyecto; no aporta ventajas sobre funciones puras |
| **D. Lógica de consulta incrustada en `main()` usando funciones locales** | Permanece en un solo fichero | Las funciones locales no son importables ni testeables directamente; sigue acoplada a la carga del fichero | Mismos problemas de testabilidad que la opción B; la visibilidad limitada de las funciones locales es una desventaja adicional |

---

## Consecuencias

**Positivas**

- Las cuatro funciones (`total_mensual`, `total_por_categoria`, `filtrar_por_categoria`,
  `ordenar_por_importe`) se pueden probar con pytest e `hypothesis` sin ningún mock
  de I/O ni de ficheros.
- Añadir nuevas consultas en el futuro (p. ej. filtrar por rango de fechas) no requiere
  tocar `gastos.py`.
- La separación de capas queda explícita en la estructura de ficheros, lo que sirve
  como documentación viva de la arquitectura.

**Negativas / compromisos**

- El proyecto pasa de un único fichero a dos módulos. Un estudiante que solo lee
  `gastos.py` no verá toda la lógica de consulta.
- La constante `CATEGORIAS_VALIDAS` existe en `filtros.py` pero `gastos.py` la
  referencia para validar entradas del menú; hay un acoplamiento implícito entre
  ambos módulos que deberá mantenerse sincronizado.
- `gastos.py` sigue conteniendo lógica de validación de entradas (mes fuera de rango,
  categoría inválida) que no vive en `filtros.py`; esta división puede resultar
  contraintuitiva hasta que se entiende el modelo de capas.
---
