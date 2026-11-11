# Support Bot — n8n + RAG + escalamiento a humano

Asistente de soporte al cliente con IA, construido con **n8n**, **Postgres/pgvector** y **Gemini**. Responde solo con la base de conocimiento y cita sus fuentes. Pasa la conversación a una persona cuando corresponde y registra cada turno para medir cuánto resuelve de verdad.

> La empresa del demo, **Tienda Nexo**, y todos sus datos son ficticios. Para usar el bot con otro negocio, reemplaza los archivos Markdown de [`kb/`](kb/) y vuelve a ejecutar el flujo de carga.

*[English version](README.md)*

## Qué hace

- **Respuestas con fuente:** busca las secciones relevantes y el modelo responde solo con ellas, con montos y plazos exactos. Cada respuesta indica qué secciones usó.
- **Búsqueda híbrida:** combina la búsqueda de texto de Postgres en español con la búsqueda semántica de pgvector (fusión por ranking recíproco). Si fallan los embeddings, sigue funcionando por palabras clave.
- **Escalamiento a humano:** escala cuando el cliente pide una persona, cuando el caso requiere revisar la cuenta o un pago (cobro doble, cargo no reconocido, posible fraude, acceso perdido) o tras dos respuestas sin resolver seguidas. Cada caso queda en `bot.escalations` con su motivo.
- **Privacidad:** oculta números de tarjeta, códigos de seguridad y contraseñas *antes* de guardar el mensaje o enviarlo al modelo.
- **Resistente a prompt injection:** el texto del cliente se trata como información, no como instrucciones.
- **Métricas:** `bot.metrics_daily` reporta sesiones, **tasa de resolución sin humano**, respuestas y latencia p95.
- **Evals:** 22 casos de regresión que verifican la fuente citada, los datos obligatorios, el contenido prohibido y el escalamiento esperado.
- **Independiente del modelo:** cambiar a Claude, OpenAI u Ollama local es cambiar un nodo y su credencial.

La arquitectura, la instalación y las decisiones de diseño están en el [README en inglés](README.md).

## Inicio rápido

```bash
cp .env.example .env     # define POSTGRES_PASSWORD y N8N_ENCRYPTION_KEY
docker compose up -d
```

Después sigue los pasos 1 a 6 del [README](README.md#run-it-locally): crear la cuenta de n8n, las credenciales de Gemini (gratis en Google AI Studio) y Postgres, importar los flujos y cargar la base de conocimiento. Luego abre `web/index.html`.
