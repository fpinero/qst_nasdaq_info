# TODO

## hito 0. arranque del proyecto y criterios de arquitectura

- [x] Definir estructura base del paquete Python `src/nasdaq_scraper/` y convención de módulos (`feature/bootstrap-package-layout`).
- [x] Crear `pyproject.toml` con metadatos, dependencias iniciales y configuración de build (`feature/init-pyproject`).
- [x] Definir contrato de salida JSON con `TypedDict` o `dataclasses` y type hints estrictos (`feature/define-output-schema`).
- [x] Definir jerarquía de excepciones (`ScrapingError`, `ConnectionError`, `ElementNotFoundError`, `ParsingError`) (`feature/custom-exceptions`).
- [x] Configurar logger de librería con niveles y formato no ruidoso por defecto (`feature/logging-baseline`).

## hito 1. reconocimiento del sitio Nasdaq y estrategia de extracción

- [x] Implementar script de reconnaissance para `baba`, `aapl`, `msft` y registrar evidencias de renderizado (HTML estático vs JS) (`feature/recon-rendering-check`).
- [x] Inspeccionar tráfico de red y verificar si existe endpoint JSON utilizable para precio y tablas ETF (`feature/recon-api-discovery`).
- [x] Identificar y documentar selectores candidatos para precio, cambio, porcentaje y encabezados de tablas (`feature/recon-selector-map`).
- [x] Definir estrategia final en documento técnico: `requests+bs4` si alcanza, `Playwright` como fallback si falta contenido (`feature/decide-scraping-strategy`).

## hito 2. capa HTTP o browser con evasión de bloqueos

- [x] Implementar generador rotativo de User-Agent con lista controlada y validada (`feature/ua-rotation`).
- [x] Implementar rotación de cabeceras realistas (`Accept`, `Accept-Language`, `Referer`, etc.) (`feature/header-rotation`).
- [x] Implementar cliente HTTP con timeout, retries y backoff exponencial con jitter (`feature/http-client-resilient`).
- [x] Añadir delay aleatorio corto entre solicitudes para reducir patrón bot (`feature/polite-random-delay`).
- [x] Implementar detector de bloqueo (`403`, `429`, challenge pages, contenido vacío anómalo) (`feature/block-detection`).
- [x] Implementar fallback opcional a Playwright con contexto variable (`viewport`, `locale`, `timezone`) (`feature/playwright-fallback-context`).
- [x] Integrar modo stealth en Playwright y validación básica de carga (`feature/playwright-stealth`).
- [x] Exponer configuración de red y anti-bot por parámetros sin hardcodear secretos (`feature/network-config-surface`).

## hito 3. parsing de datos de cotización

- [ ] Implementar parser de precio (`price`) robusto a moneda, separadores y espacios (`feature/extract-price`).
- [ ] Implementar parser de cambio absoluto (`change`) soportando `+` y `-` (`feature/extract-change`).
- [ ] Implementar parser de porcentaje (`change_percent`) removiendo `%` y normalizando a float (`feature/extract-change-percent`).
- [ ] Implementar normalizadores numéricos reutilizables (`parse_money`, `parse_percent`) (`feature/number-normalizers`).
- [ ] Añadir validación de sanidad para campos de cotización y errores explícitos si faltan (`feature/quote-validation`).

## hito 4. parsing de tablas ETF y unificación

- [ ] Implementar localizador de tabla con encabezado exacto `Nasdaq Listed ETFs where {TICKER} is a top 10 holding` (`feature/find-primary-etf-table`).
- [ ] Implementar localizador de tabla alternativa de encabezado similar `ETFs with {TICKER} as a Top 10 Holding` (`feature/find-secondary-etf-table`).
- [ ] Implementar extractor de filas para `symbol`, `name`, `weighting` en la primera tabla (`feature/extract-etf-rows-primary`).
- [ ] Implementar extractor de filas para la segunda tabla ignorando `100 Day Price Change (%)` (`feature/extract-etf-rows-secondary`).
- [ ] Unificar filas de ambas tablas en una sola lista `etfs`, preservando orden estable (`feature/merge-etf-lists`).
- [ ] Implementar deduplicación opcional por `symbol+name` si aparecen repetidos en ambas tablas (`feature/dedupe-etfs`).
- [ ] Manejar caso sin ETFs, devolviendo `etfs: []` sin lanzar error (`feature/empty-etf-list-handling`).

## hito 5. API pública de la librería

- [ ] Implementar `get_ticker_data(ticker: str) -> dict` como punto único de entrada (`feature/public-api-get-ticker-data`).
- [ ] Añadir validación de input de ticker (normalización a minúsculas, caracteres permitidos) (`feature/ticker-input-validation`).
- [ ] Orquestar flujo completo `fetch -> parse -> validate -> build output JSON` (`feature/orchestrate-scraping-pipeline`).
- [ ] Garantizar ausencia de caché interna (sin Redis ni almacenamiento local) (`feature/no-cache-guarantee`).
- [ ] Documentar errores lanzados por la API pública con mensajes accionables (`feature/public-error-contract`).

## hito 6. calidad y pruebas

- [ ] Crear suite unitaria para normalizadores y parseadores numéricos (`feature/unit-tests-normalizers`).
- [ ] Crear tests de parsing HTML con fixtures de estructura real para cotización y ETFs (`feature/unit-tests-html-parsers`).
- [ ] Crear tests de integración online para `baba`, `aapl`, `msft` con aserciones mínimas estables (`feature/integration-tests-tickers`).
- [ ] Crear test de regresión para caso de página sin tablas ETF (`feature/integration-test-no-etfs`).
- [ ] Crear test de resiliencia de red: timeout, retry agotado, bloqueo detectado (`feature/network-error-tests`).
- [ ] Configurar lint, type-check y cobertura mínima para merge (`feature/quality-gates`).

## hito 7. entregables finales y experiencia de uso

- [ ] Escribir `README.md` en inglés con instalación, uso, errores y notas de Playwright (`feature/readme-english`).
- [ ] Crear `example.py` que invoque `get_ticker_data("baba")` e imprima JSON (`feature/add-example-script`).
- [ ] Añadir instrucciones de instalación de navegadores Playwright si se habilita fallback browser (`feature/playwright-install-docs`).
- [ ] Generar `requirements.txt` o mantener dependencias solo en `pyproject.toml` y dejar una decisión única y consistente (`feature/dependencies-finalize`).
- [ ] Añadir guía breve de troubleshooting de scraping y logging en README (`feature/docs-troubleshooting`).
- [ ] Preparar checklist de release local: tests, ejemplo funcional, paquete importable (`feature/release-readiness-checklist`).

## hito 8. estrategia de ramas y commits

- [ ] Definir convención de ramas por tarea atómica (`feature/<scope>`) (`feature/git-workflow-definition`).
- [ ] Definir plantilla de commit messages en inglés (`feat`, `fix`, `chore`, `docs`, `test`) (`feature/commit-template-english`).
- [ ] Definir criterios de PR por tarea: alcance pequeño, evidencia de prueba, sin mezcla de responsabilidades (`feature/pr-quality-rules`).
