Fecha: 2026-03-09
Hecho:
- Se inició hito 7 y se completaron entregables de documentación y experiencia de uso.
- Se reescribió `README.md` en inglés con instalación, setup de Playwright, uso, contrato de salida, errores y troubleshooting.
- Se añadió `example.py` para ejecutar `get_ticker_data("baba")` y mostrar JSON formateado.
- Se documentó checklist de release local en `docs/release_checklist.md`.
- Se definió de forma explícita que `pyproject.toml` es la única fuente de verdad de dependencias.
Archivos tocados:
- README.md
- example.py
- docs/release_checklist.md
- TODO.md
- avances.md
Decisiones:
- Mantener dependencias centralizadas solo en `pyproject.toml` para evitar drift con un `requirements.txt` duplicado.
- Mantener setup browser documentado (`chromium`, `firefox`) como paso recomendado para extracción ETF estable.
Deuda técnica / pendientes:
- Iniciar hito 8 con documentación del flujo de ramas y estándares de PR/commits.

Fecha: 2026-03-09
Hecho:
- Se inició y completó el hito 6 con una base de calidad y pruebas para el scraper.
- Se añadieron tests unitarios de parsing numérico en `tests/unit/test_parsing.py`.
- Se añadieron tests unitarios del parser ETF con fixture hidratada en `tests/unit/test_etf_parser.py` y `tests/fixtures/etf_tables_hydrated.html`.
- Se añadieron tests de resiliencia de red y anti-bloqueo para transporte en `tests/unit/test_transport.py`.
- Se añadieron tests de integración online en `tests/integration/test_live_tickers.py` para `baba`, `aapl`, `msft` y validación del contrato `etfs` lista.
- Se añadió configuración de pytest en `pyproject.toml` (testpaths y marker `integration`).
- Se ejecutaron gates de calidad en `.venv`: ruff, mypy, tests unitarios e integración online.
Archivos tocados:
- tests/unit/test_parsing.py
- tests/unit/test_etf_parser.py
- tests/unit/test_transport.py
- tests/unit/test_scraper_contract.py
- tests/integration/test_live_tickers.py
- tests/fixtures/etf_tables_hydrated.html
- pyproject.toml
- src/nasdaq_scraper/transport.py
- TODO.md
- avances.md
Decisiones:
- Mantener tests online protegidos por `RUN_LIVE_TESTS=1` para evitar flakiness en ejecuciones locales por defecto.
- Usar aserciones estables de estructura y tipos en integración, evitando checks frágiles de valores absolutos.
- Mantener quality gates mínimos obligatorios: `ruff check`, `mypy`, y `pytest`.
Deuda técnica / pendientes:
- Añadir `pytest-cov` y umbral formal de cobertura cuando se cierre hito 7.

Fecha: 2026-03-09
Hecho:
- Se inició hito 5 y se consolidó `get_ticker_data` como API pública estable del paquete.
- Se mejoraron mensajes de error accionables para fallos de red y payload (`ConnectionError`, `ElementNotFoundError`, `ParsingError`).
- Se documentó explícitamente el contrato público en `docs/public_api_contract.md`.
- Se dejó explícito en docstring de la API que la librería no implementa caché interna.
Archivos tocados:
- src/nasdaq_scraper/scraper.py
- docs/public_api_contract.md
- TODO.md
- avances.md
Decisiones:
- Mantener `get_ticker_data` como único punto de entrada de consumo externo.
- Exponer errores específicos con contexto de ticker para facilitar debug en la app padre.
- Mantener política de datos frescos, sin Redis ni cache local en esta librería.
Deuda técnica / pendientes:
- Avanzar con hito 6 para cubrir el contrato público con tests unitarios e integración.

Fecha: 2026-03-09
Hecho:
- Se ajustó el hito 4 con workaround explícito para tablas ETF renderizadas por JavaScript.
- Se instalaron dependencias browser en entorno virtual (`.venv`) y navegadores Playwright (`chromium`, `firefox`) para validar extracción dinámica real.
- Se detectó y resolvió incompatibilidad de `playwright-stealth` usando API moderna basada en `Stealth().apply_stealth_sync`.
- Se añadió fallback de navegador en Playwright (`chromium` -> `firefox`) para evitar `ERR_HTTP2_PROTOCOL_ERROR` observado con Chromium contra Nasdaq.
- Se implementó extracción de ETFs en `src/nasdaq_scraper/etf.py`.
- Se añadieron localizadores para los dos bloques de tabla ETF dentro del componente `jupiter22-etf-stocks-holdings-bar-chart-table`.
- Se implementó extracción de filas (`symbol`, `name`, `weighting`) ignorando la columna de cambio de precio cuando existe.
- Se integró unificación y deduplicación por `symbol+name`, preservando orden de aparición.
- Se conectó la extracción ETF en `get_ticker_data` con estrategia Playwright-first para esperar filas hidratadas y fallback HTTP si Playwright no está disponible o no devuelve datos.
- Se validó extracción end-to-end con resultados reales de ETFs para `baba`, `aapl` y `msft`.
- Se mantiene retorno seguro con `etfs: []` cuando no se puede obtener contenido de tablas.
Archivos tocados:
- src/nasdaq_scraper/etf.py
- src/nasdaq_scraper/scraper.py
- src/nasdaq_scraper/__init__.py
- docs/package_architecture.md
- TODO.md
- avances.md
Decisiones:
- Se usa parsing basado en clases CSS estables del componente ETF para minimizar dependencia de texto exacto localizado.
- Se mantiene compatibilidad con ambos layouts de tabla (con y sin columna de 100-day change).
- Se adopta Playwright-first para ETF, dado que el HTML inicial suele traer skeleton sin datos finales.
- Se usa Firefox como segundo motor automático cuando Chromium falla por protocolo HTTP/2 en este entorno.
Deuda técnica / pendientes:
- Añadir pruebas unitarias para el parser ETF con fixtures de HTML renderizado.

Fecha: 2026-03-09
Hecho:
- Se conectó la capa de transporte del hito 2 al flujo de extracción de cotización del hito 3.
- Se implementó `src/nasdaq_scraper/parsing.py` con normalizadores `parse_money`, `parse_change` y `parse_percent`.
- Se implementó `src/nasdaq_scraper/scraper.py` con `get_ticker_data(ticker)` usando `NasdaqHttpClient` contra `api.nasdaq.com`.
- Se añadió validación de entrada de ticker, validación de presencia de campos requeridos y validación de finitud numérica.
- Se expuso la API pública y parsers desde `src/nasdaq_scraper/__init__.py`.
Archivos tocados:
- src/nasdaq_scraper/parsing.py
- src/nasdaq_scraper/scraper.py
- src/nasdaq_scraper/__init__.py
- docs/package_architecture.md
- TODO.md
- avances.md
Decisiones:
- Se adopta `api.nasdaq.com/api/quote/{SYMBOL}/info?assetclass=STOCKS` como fuente primaria para `price`, `change` y `change_percent`.
- Se devuelve `etfs: []` como placeholder controlado hasta completar los hitos de extracción ETF.
- El flujo lanza excepciones específicas (`ElementNotFoundError`, `ParsingError`) cuando faltan campos o fallan conversiones.
Deuda técnica / pendientes:
- Implementar extracción y unificación de tablas ETF (hito 4).

Fecha: 2026-03-09
Hecho:
- Se inició y completó la base técnica del hito 2 en `src/nasdaq_scraper/transport.py`.
- Se implementó rotación de User-Agent y cabeceras browser-like mediante `UserAgentRotator` y `build_browser_headers`.
- Se implementó cliente HTTP resiliente `NasdaqHttpClient` con timeout, retries, backoff exponencial, jitter y delay aleatorio entre peticiones.
- Se añadió detección de bloqueo por códigos HTTP y patrones en cuerpo de respuesta (`detect_blocking`).
- Se implementó fallback opcional con Playwright (`fetch_with_playwright_fallback`) con variación de `viewport`, `locale`, `timezone` y `user_agent`.
- Se integró soporte opcional de stealth (`playwright-stealth`) cuando la dependencia está disponible.
- Se expuso configuración parametrizable mediante `TransportConfig` para evitar valores hardcodeados en el flujo de scraping.
Archivos tocados:
- src/nasdaq_scraper/transport.py
- src/nasdaq_scraper/__init__.py
- docs/package_architecture.md
- TODO.md
- avances.md
Decisiones:
- La capa de transporte se implementa con `urllib` estándar para no depender de instalación runtime de terceros en esta etapa.
- Playwright se mantiene como fallback opcional y desacoplado, activable solo cuando se necesite extracción dinámica.
- La detección de bloqueo se modela como señal explícita para reintento controlado y observabilidad.
Deuda técnica / pendientes:
- Conectar `NasdaqHttpClient` y fallback Playwright con el pipeline funcional de `get_ticker_data` en hitos 3 a 5.

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
