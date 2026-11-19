# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Normalized validation models with Pydantic (`schemas/ac.py` and `schemas/session.py`):
  - `LoginRequest`, `AcStatus`, and `AcCommand`.
  - Strict literal types for supported brands (`BrandType`), work modes (`WorkModeType`), fan speeds (`FanSpeedType`), and louver swing (`SwingType`).
  - Target temperature bounds validation (16°C to 30°C).
- Added `msmart-ng` dependency for local LAN communication (M-Smart V3 protocol) with Midea appliances.
- Added modern project configuration file (`pyproject.toml`) for Python package metadata and version tracking.
- Comprehensive Midea diagnostic, discovery, and setup documentation in `api-python/README.md`.

### Changed
- Refactored settings module into a dedicated `config/` package using `pydantic-settings`.

---

## [0.1.0] - 2026-11-17

### Added
- Initial monorepo layout containing:
  - `api-python`: FastAPI backend/sidecar service.
  - `frontend-vue`: Vue 3 + Tailwind CSS desktop UI.
  - `src-tauri`: Tauri v2 Windows desktop shell scaffolding.
  - `backend-java`: Reserved workspace for future Java microservice migration.
- Initial Hisense cloud integration via `connectlife`:
  - `GET /status` endpoint to fetch primary appliance state.
  - `POST /control` endpoint to send appliance commands.
- Local CORS policy configured for `localhost:5173` and `tauri://localhost`.
- Architecture and technical overview documentation in `README.md`.
