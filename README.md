# BTC Price Monitor — 2H

Automatización independiente para consultar Bitcoin aproximadamente cada 2 horas.

## Fuentes

Principales:
- CoinGecko
- Coinbase
- Kraken
- Binance

Respaldos:
- Bitstamp
- CryptoCompare

El monitor intenta conservar **4 fuentes válidas**. Si una fuente principal falla, incorpora una fuente de respaldo. Si no puede obtener al menos cuatro precios válidos, la ejecución falla en lugar de enviar un reporte incompleto.

## Notificaciones

Envía el reporte a Gmail y Telegram mediante una capa de notificación configurada por secretos de GitHub.

## Programación

GitHub Actions ejecuta el workflow mediante `0 */2 * * *` (UTC). Las ejecuciones programadas pueden retrasarse ocasionalmente por la disponibilidad de GitHub Actions; no debe interpretarse como una garantía de exactitud al minuto.

## Seguridad

No se guardan tokens ni contraseñas en el código. Las credenciales deben configurarse como GitHub Actions Secrets.
