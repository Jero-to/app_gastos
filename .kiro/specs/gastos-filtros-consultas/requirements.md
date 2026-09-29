# Documento de Requisitos

## Introducción

Esta feature añade capacidades de consulta y filtrado a la aplicación de registro de gastos por consola. Las nuevas funcionalidades permiten al usuario obtener totales mensuales, desglosar gastos por categoría, filtrar por categoría y ordenar por importe. Toda la lógica de consulta se encapsula en un módulo independiente `filtros.py` con funciones puras, sin efectos secundarios. El menú de `gastos.py` se amplía con las nuevas opciones sin romper el comportamiento existente.

## Glosario

- **App**: La aplicación de registro de gastos por consola (`gastos.py`).
- **Gasto**: Diccionario Python con los campos `descripcion` (str), `cantidad` (float), `categoria` (str) y `fecha` (str en formato "AAAA-MM-DD").
- **Lista_Gastos**: Lista de objetos Gasto cargada desde `gastos.json`.
- **Filtros**: Módulo `filtros.py` que expone funciones puras de consulta y filtrado.
- **Menu**: La función `main()` de `gastos.py` que presenta las opciones al usuario e invoca la lógica correspondiente.
- **Categoria_Valida**: Uno de los cinco valores permitidos: `Alimentacion`, `Transporte`, `Ocio`, `Salud`, `Otros`.
- **Mes_Valido**: Entero en el rango 1–12 inclusive.
- **Total_Mensual**: Suma de las cantidades de todos los Gastos cuya fecha corresponde a un año y mes dados, redondeada a 2 decimales.
- **Total_Por_Categoria**: Diccionario que mapea cada Categoria_Valida a la suma de las cantidades de los Gastos de esa categoría, redondeada a 2 decimales.

---

## Requisitos

### Requisito 1: Total mensual de gastos

**User Story:** Como usuario, quiero conocer el importe total gastado en un mes y año concretos, para controlar mis finanzas mensuales.

#### Criterios de Aceptación

1. WHEN el usuario proporciona un año y un Mes_Valido, THE Filtros SHALL devolver el Total_Mensual calculando la suma de las cantidades de todos los Gastos cuya fecha corresponde a ese año y mes, redondeada a 2 decimales.
2. WHEN el usuario proporciona un año y un Mes_Valido para los cuales no existen Gastos, THE Filtros SHALL devolver 0.00.
3. IF el usuario proporciona un mes fuera del rango 1–12, THEN THE Menu SHALL mostrar un mensaje de error indicando que el mes debe estar entre 1 y 12, sin realizar ningún cálculo.
4. IF el usuario proporciona un año no numérico, THEN THE Menu SHALL mostrar un mensaje de error indicando que el año debe ser un número entero, sin realizar ningún cálculo.

---

### Requisito 2: Total de gastos por categoría

**User Story:** Como usuario, quiero ver cuánto he gastado en cada categoría, opcionalmente acotado a un mes, para identificar en qué áreas gasto más.

#### Criterios de Aceptación

1. WHEN el usuario solicita el total por categoría sin restringir a un mes, THE Filtros SHALL devolver un Total_Por_Categoria que incluye todas las Categoria_Validas presentes en la Lista_Gastos.
2. WHEN el usuario solicita el total por categoría restringido a un año y Mes_Valido, THE Filtros SHALL devolver un Total_Por_Categoria calculado únicamente con los Gastos cuya fecha corresponde a ese año y mes.
3. WHEN la Lista_Gastos no contiene Gastos para una Categoria_Valida, THE Filtros SHALL omitir esa categoría del diccionario resultado (el diccionario resultado no incluye entradas con valor 0.00).
4. THE Filtros SHALL redondear cada valor del Total_Por_Categoria a 2 decimales.
5. IF el usuario proporciona un mes fuera del rango 1–12 al filtrar por mes, THEN THE Menu SHALL mostrar un mensaje de error indicando que el mes debe estar entre 1 y 12, sin realizar ningún cálculo.

---

### Requisito 3: Filtrar gastos por categoría

**User Story:** Como usuario, quiero ver únicamente los gastos de una categoría concreta, para revisar mis hábitos en un área específica.

#### Criterios de Aceptación

1. WHEN el usuario proporciona una Categoria_Valida, THE Filtros SHALL devolver una lista con todos los Gastos cuya categoría coincide exactamente con el valor proporcionado.
2. WHEN no existen Gastos para la Categoria_Valida proporcionada, THE Filtros SHALL devolver una lista vacía.
3. IF el usuario proporciona un valor que no corresponde a ninguna Categoria_Valida, THEN THE Menu SHALL mostrar un mensaje de error indicando las categorías válidas disponibles, sin invocar ninguna función de Filtros.
4. THE Filtros SHALL preservar el orden original de los Gastos en la lista resultado.

---

### Requisito 4: Ordenar gastos por importe

**User Story:** Como usuario, quiero ver los gastos ordenados por su importe, para identificar rápidamente los más costosos o los más económicos.

#### Criterios de Aceptación

1. WHEN el usuario solicita ordenar sin especificar dirección, THE Filtros SHALL devolver una nueva lista de Gastos ordenada de mayor a menor cantidad.
2. WHEN el usuario solicita ordenar en dirección ascendente, THE Filtros SHALL devolver una nueva lista de Gastos ordenada de menor a mayor cantidad.
3. THE Filtros SHALL devolver una nueva lista sin modificar la Lista_Gastos original.
4. WHEN la Lista_Gastos está vacía, THE Filtros SHALL devolver una lista vacía.

---

### Requisito 5: Módulo filtros.py con funciones puras

**User Story:** Como desarrollador, quiero que toda la lógica de consulta esté encapsulada en funciones puras en `filtros.py`, para facilitar el testing y el mantenimiento.

#### Criterios de Aceptación

1. THE Filtros SHALL exponer las siguientes funciones públicas: `total_mensual`, `total_por_categoria`, `filtrar_por_categoria` y `ordenar_por_importe`.
2. THE Filtros SHALL implementar cada función como función pura: sin llamadas a `input()`, sin llamadas a `print()`, sin acceso al sistema de ficheros y sin modificar los argumentos recibidos.
3. THE Filtros SHALL aceptar como primer argumento de todas sus funciones una Lista_Gastos arbitraria, de forma que puedan ser invocadas con cualquier conjunto de datos sin depender del fichero `gastos.json`.

---

### Requisito 6: Integración en el menú de gastos.py

**User Story:** Como usuario, quiero acceder a las nuevas consultas desde el menú principal de la aplicación, para poder usarlas sin conocer los detalles de implementación.

#### Criterios de Aceptación

1. THE Menu SHALL presentar opciones numeradas para cada una de las cuatro nuevas funcionalidades (total mensual, total por categoría, filtrar por categoría, ordenar por importe), manteniendo la opción "Salir" como última opción del menú.
2. THE Menu SHALL mantener el comportamiento existente de las opciones añadir gasto, listar gastos y eliminar gasto sin modificación funcional.
3. WHEN el usuario selecciona una nueva opción del menú, THE Menu SHALL solicitar los parámetros necesarios, invocar la función correspondiente de Filtros con la Lista_Gastos actual y mostrar el resultado por consola.
4. THE App SHALL utilizar el bloque `if __name__ == "__main__": main()` para invocar la función principal, en lugar de una llamada directa a `main()`.

---

### Requisito 7: Robustez ante entradas inválidas en el menú

**User Story:** Como usuario, quiero que el menú me informe claramente cuando introduzco un dato incorrecto, para poder corregirlo sin que la aplicación falle.

#### Criterios de Aceptación

1. IF el usuario introduce un mes fuera del rango 1–12 en cualquier opción del menú que lo requiera, THEN THE Menu SHALL mostrar el mensaje "Error: el mes debe ser un número entero entre 1 y 12." sin provocar una excepción no capturada.
2. IF el usuario introduce una categoría que no es una Categoria_Valida en cualquier opción del menú que la requiera, THEN THE Menu SHALL mostrar el mensaje "Error: categoría no válida. Las categorías válidas son: Alimentacion, Transporte, Ocio, Salud, Otros." sin provocar una excepción no capturada.
3. IF el usuario introduce un valor no numérico donde se espera un número entero (año o mes), THEN THE Menu SHALL mostrar el mensaje "Error: se esperaba un número entero." sin provocar una excepción no capturada.
4. WHILE el menú está activo, THE Menu SHALL retornar al bucle principal del menú tras mostrar cualquier mensaje de error, permitiendo al usuario intentarlo de nuevo.
