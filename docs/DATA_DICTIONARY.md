# Diccionario de datos

| Campo | Tipo | Descripción |
|---|---|---|
| `order_id` | texto | Identificador único del pedido |
| `order_date` | fecha | Fecha de la operación |
| `store_id` | texto | Clave de sucursal |
| `region` | texto | Región comercial de México |
| `channel` | texto | Tienda u Online |
| `category` | texto | Familia del producto |
| `product` | texto | Nombre del producto |
| `units` | entero | Unidades vendidas |
| `unit_price` | decimal | Precio unitario antes de descuento |
| `discount_pct` | decimal | Descuento entre 0 y 0.50 |
| `unit_cost` | decimal | Costo unitario simulado |
| `customer_segment` | texto | Nuevo, Recurrente o Empresa |
| `payment_method` | texto | Medio de pago |
| `returned` | booleano | Indica devolución del pedido |
| `satisfaction` | entero | Evaluación de 1 a 5 |
| `gross_sales` | decimal | Unidades × precio |
| `discount_amount` | decimal | Importe descontado |
| `net_sales` | decimal | Venta después de descuento |
| `total_cost` | decimal | Unidades × costo |
| `gross_profit` | decimal | Venta neta menos costo |
| `margin_pct` | decimal | Utilidad como porcentaje de venta |
| `is_high_value_order` | booleano | Pedido superior al límite IQR |
