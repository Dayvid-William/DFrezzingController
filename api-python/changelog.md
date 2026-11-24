# Changelog — Backend (DFrezzingController)

All notable changes to the Python/FastAPI local backend service (`api-python`) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
* Automatic session token refresh and reconnection fallback for cloud/LAN timeouts.
* Background polling optimization and rate-limiting protection for device status queries.
* Bundling the Python runtime as a standalone sidecar executable for Tauri v2 desktop distribution.

---

## [0.1.0] - 2026-11-24

### Added
* Initialized local REST API server using **Python 3.12**, **FastAPI**, and **Uvicorn** (`http://127.0.0.1:8000`).
* Designed unified multi-brand REST contract supporting:
  * `GET /health` — Server availability and active local session inspection.
  * `POST /auth/login` — Multi-brand authentication and device discovery.
  * `POST /auth/logout` — Session termination and local credential cleanup.
  * `GET /ac/status` — Normalized telemetry and device capability reporting.
  * `POST /ac/command` — Unified climate state updates (power, target temperature, mode, fan speed, swing, eco, and sleep).
* Integrated **Hisense** driver powered by `connectlife`.
* Integrated **Midea / SmartHome** driver powered by `msmart-ng` with LAN discovery and optional manual local IP override.
* Implemented local session persistence (`session.json`) to retain authenticated device context across restarts.
* Configured `CORSMiddleware` allowing local development (`http://localhost:5173`, `http://127.0.0.1:5173`) and Tauri desktop origins (`tauri://localhost`, `http://tauri.localhost`).
* Added global exception handler to classify authentication and cloud error codes (`401`, `3101`, `3102`) into structured JSON `401` responses while preserving CORS headers.

### Fixed
* Fixed `CORSMiddleware` keyword argument typo (`allow_credntials` $\rightarrow$ `allow_credentials=True`) causing `500 Internal Server Error` on preflight `OPTIONS` requests.