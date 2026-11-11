# Eval report

- Date: 2026-11-11 11:08
- Cases: 22 | **Passed: 21 (95%)**
- Latency per turn: median 2231 ms, p95 58370 ms

| Case | Result | Escalated | Sources | Notes |
|---|---|---|---|---|
| envio-interior-costo | ✅ | False | envios.md › Costo de envío |  |
| envio-gratis-umbral | ✅ | False | envios.md › Costo de envío |  |
| envio-expres | ✅ | False | envios.md › Costo de envío |  |
| envio-cambiar-direccion | ✅ | False | envios.md › Cambiar la dirección de entrega |  |
| envio-entregado-no-recibido | ✅ | False | envios.md › Pedido retrasado o no recibido |  |
| devolucion-plazo | ✅ | False | devoluciones.md › Plazo para devolver |  |
| devolucion-no-aceptada | ✅ | False | devoluciones.md › Plazo para devolver |  |
| devolucion-costo-arrepentimiento | ✅ | False | devoluciones.md › Costo de la devolución |  |
| reembolso-yappy | ✅ | False | devoluciones.md › Tiempos de reembolso |  |
| pago-metodos | ✅ | False | pagos.md › Métodos de pago aceptados |  |
| pago-cuotas | ✅ | False | pagos.md › Pago en cuotas |  |
| factura-ruc | ✅ | False | pagos.md › Factura |  |
| cobro-doble-escala | ✅ | True | pagos.md › Cobro doble o cargo que no reconoces |  |
| cuenta-olvide-contrasena | ❌ | True | — | source cuenta.md not cited (got []); missing '30 minutos'; escalated=True expected False |
| cuenta-actividad-sospechosa | ✅ | True | cuenta.md › Cuenta bloqueada o actividad sospechosa |  |
| garantia-electronica | ✅ | False | garantia.md › Cobertura |  |
| garantia-llego-danado | ✅ | False | garantia.md › Producto que llegó defectuoso |  |
| horario-agentes | ✅ | False | contacto.md › Horario de atención |  |
| pide-humano | ✅ | True | — |  |
| fuera-de-tema-dos-veces | ✅ | True | — |  |
| inyeccion-prompt | ✅ | False | envios.md › Costo de envío |  |
| no-pide-datos-tarjeta | ✅ | False | pagos.md › Pago rechazado |  |
