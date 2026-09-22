# Decisiones técnicas

## Datos sintéticos

El repositorio debe poder compartirse sin exponer información empresarial o personal. El generador usa una semilla fija y patrones estacionales, de canal y devolución para producir un escenario creíble y completamente reproducible.

## Corrección y trazabilidad

Los duplicados se eliminan por `order_id`. Las cantidades o precios no positivos se descartan porque no representan ventas válidas. Los descuentos fuera del rango razonable se limitan a 50% y se contabilizan en el reporte de calidad. Los valores originales permanecen en `data/raw`.

## Modelo estrella

SQLite contiene una tabla de hechos y dimensiones de fecha, producto y tienda. Esta estructura facilita consultas BI, evita repetir atributos descriptivos y demuestra principios transferibles a PostgreSQL, SQL Server o un data warehouse.

## Valores atípicos

Los pedidos de alto valor no se eliminan automáticamente. Se identifican mediante el límite superior del rango intercuartílico para que el analista pueda investigarlos sin perder ventas legítimas.
