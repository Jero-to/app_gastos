# Tasks

- [x] 1. Crear el módulo filtros.py con las cuatro funciones puras
  - Crear fichero `filtros.py` en la raíz del proyecto
  - Constante `CATEGORIAS_VALIDAS = {"Alimentación", "Transporte", "Ocio", "Salud", "Otros"}`
  - Función privada `_misma_fecha(fecha_str, anio, mes) -> bool`
  - Función `total_mensual(gastos, anio, mes) -> float` — suma cantidades del mes, round 2 dec, devuelve 0.0 si no hay gastos
  - Función `total_por_categoria(gastos, anio=None, mes=None) -> dict` — agrupa por categoría, opcionalmente filtrada por mes, omite categorías con 0 gastos, redondea a 2 dec
  - Función `filtrar_por_categoria(gastos, categoria) -> list` — devuelve lista filtrada, preserva orden
  - Función `ordenar_por_importe(gastos, ascendente=False) -> list` — devuelve lista nueva ordenada, no muta original
  - Ninguna función llama a input(), print() ni accede a ficheros
  - **Files:** filtros.py

- [x] 2. Crear tests unitarios y de propiedad
  - Crear directorio tests/ y fichero tests/__init__.py vacío
  - Crear tests/test_filtros.py con tests pytest: test_total_mensual_con_gastos, test_total_mensual_mes_sin_gastos, test_total_mensual_redondeo, test_total_por_categoria_global, test_total_por_categoria_con_mes, test_total_por_categoria_omite_vacias, test_filtrar_por_categoria_devuelve_correctos, test_filtrar_por_categoria_lista_vacia, test_filtrar_por_categoria_preserva_orden, test_ordenar_descendente_por_defecto, test_ordenar_ascendente, test_ordenar_no_modifica_original, test_ordenar_lista_vacia
  - Tests de propiedad con hypothesis: test_prop_total_mensual_igual_suma_manual, test_prop_filtrar_tamano_menor_o_igual, test_prop_total_categoria_consistente_con_filtrar, test_prop_ordenar_mismo_contenido, test_prop_ordenar_no_muta_original, test_prop_filtrar_idempotente
  - NO ejecutar los tests, solo escribirlos
  - **Files:** tests/__init__.py, tests/test_filtros.py
  - depends_on: [1]

- [x] 3. Modificar gastos.py — punto de entrada y menú ampliado
  - Sustituir llamada final `main()` por `if __name__ == "__main__": main()`
  - Añadir `import filtros` al inicio
  - Añadir opción "Total mensual": pedir año y mes, validar, llamar filtros.total_mensual, mostrar resultado
  - Añadir opción "Total por categoría": preguntar si filtrar por mes, llamar filtros.total_por_categoria, mostrar resultado
  - Añadir opción "Filtrar por categoría": pedir categoría, validar contra filtros.CATEGORIAS_VALIDAS, llamar filtros.filtrar_por_categoria, mostrar resultado
  - Añadir opción "Ordenar por importe": preguntar dirección, llamar filtros.ordenar_por_importe, mostrar resultado
  - Salir siempre como última opción del menú
  - Validaciones: mes fuera de 1-12 → "Error: el mes debe ser un número entero entre 1 y 12.", categoría inválida → "Error: categoría no válida. Las categorías válidas son: Alimentación, Transporte, Ocio, Salud, Otros.", valor no numérico → "Error: se esperaba un número entero."
  - **Files:** gastos.py
  - depends_on: [1]

- [x] 4. Verificación de no-regresión del comportamiento existente
  - Crear tests/test_gastos_menu.py con tests que verifiquen que añadir, listar y eliminar siguen funcionando
  - Usar mock de input() y captura de stdout con capsys de pytest
  - NO ejecutar los tests, solo escribirlos
  - **Files:** tests/test_gastos_menu.py
  - depends_on: [2, 3]
