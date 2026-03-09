Fecha: 2026-03-09
Hecho:
- Se completó el hito 1 con reconnaissance automatizada para `baba`, `aapl` y `msft`.
- Se implementó `src/nasdaq_scraper/recon.py` para inspección de renderizado, extracción de `ApiSettings` embebidos y sondeo de endpoints de quote.
- Se añadió `scripts/recon_nasdaq.py` para generar reportes reproducibles en JSON y Markdown.
- Se generaron artefactos de reconnaissance en `docs/reconnaissance/findings.json` y `docs/reconnaissance/findings.md`.
- Se documentaron selectores candidatos y estrategia técnica en `docs/reconnaissance/selector_map.md` y `docs/reconnaissance/strategy.md`.
- Se verificó que `https://api.nasdaq.com/api/quote/{SYMBOL}/info?assetclass=STOCKS` responde con JSON útil para `price`, `change` y `change_percent`.
Archivos tocados:
- src/nasdaq_scraper/recon.py
- src/nasdaq_scraper/__init__.py
- scripts/recon_nasdaq.py
- docs/reconnaissance/findings.json
- docs/reconnaissance/findings.md
- docs/reconnaissance/selector_map.md
- docs/reconnaissance/strategy.md
- docs/package_architecture.md
- TODO.md
- avances.md
Decisiones:
- Estrategia para cotización: API-first usando `api.nasdaq.com`, con HTML como fallback estructural.
- Estrategia para ETFs: mantener selectores por encabezado como fallback, pero priorizar descubrimiento dinámico adicional con browser/network capture si no aparecen en HTML estático.
- Se detectó que `qcapi.nasdaq.com` devuelve 403 desde cliente directo, por lo que se usará `api.nasdaq.com` en la implementación.
Deuda técnica / pendientes:
- Iniciar hito 2 con capa de transporte robusta (headers rotativos, retry/backoff, detección de bloqueo y delays).

Fecha: 2026-03-09
Hecho:
- Se completó el hito 0 del plan.
- Se creó la base de la librería en `src/nasdaq_scraper/` con módulos separados por responsabilidad.
- Se añadió `pyproject.toml` con configuración de empaquetado, dependencias base y extras (`browser`, `dev`).
- Se definieron contratos tipados de salida (`TypedDict`), jerarquía de excepciones y utilidades de logging.
- Se documentó la convención de módulos en `docs/package_architecture.md`.
- Se validó sintaxis de `pyproject.toml` y compilación de módulos Python.
Archivos tocados:
- pyproject.toml
- src/nasdaq_scraper/__init__.py
- src/nasdaq_scraper/types.py
- src/nasdaq_scraper/exceptions.py
- src/nasdaq_scraper/log_config.py
- src/nasdaq_scraper/py.typed
- docs/package_architecture.md
- TODO.md
- avances.md
Decisiones:
- Se usa estructura `src/` y superficie pública mínima exportada desde `__init__.py`.
- Se adopta `TypedDict` para el contrato JSON de salida desde el arranque.
- Se separa configuración de logging en un módulo dedicado para evitar acoplamiento con scraping/parsing.
Deuda técnica / pendientes:
- Iniciar hito 1 con reconnaissance del sitio Nasdaq para confirmar estrategia API/HTML/Playwright.

Fecha: 2026-03-09
Hecho:
- Se leyó el documento de requisitos del scraping de Nasdaq y se extrajeron requisitos funcionales y técnicos.
- Se revisaron skills de scraping del repositorio para reutilizar técnicas de anti-bloqueo, selectores robustos y estrategia iterativa.
- Se creó un plan de desarrollo completo en `TODO.md`, dividido por hitos y tareas atómicas orientadas a ramas `feature/*`.
Archivos tocados:
- TODO.md
- avances.md
- lessons.md
Decisiones:
- Se prioriza enfoque progresivo: reconocimiento, estrategia API/HTML y fallback Playwright solo si es necesario.
- Se incluye evasión de bloqueos desde la capa de transporte: rotación de User-Agent, cabeceras realistas, retry con backoff, detección de bloqueo y delays aleatorios.
- Cada tarea del plan se define como unidad pequeña y autónoma para implementación por rama independiente.
Deuda técnica / pendientes:
- Iniciar implementación del hito 0 desde la estructura base del paquete y configuración de `pyproject.toml`.
