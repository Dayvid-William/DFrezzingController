# Changelog — Frontend (DFrezzingController)

All notable changes to the web/desktop frontend (`frontend-vue`) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
* Main climate control dashboard (`DashboardView.vue`) and modular control widgets under `src/components/`.
* Temperature controller (`16°C` to `30°C`) featuring an 8-stop dynamic thermal color gradient (blue to green to red) with no text shadow behind the primary readout.
* Operation mode selectors (`Cool`, `Heat`, `Dry`, `Fan`, `Auto`), fan speed controls, and capability-driven toggles (`Swing`, `Eco`, `Sleep`).
* Native Windows desktop packaging with Tauri v2.

---

## [0.1.0] - 2026-11-24

### Added
* Initialized frontend architecture with **Vue 3**, **TypeScript**, **Vite**, and **Lucide Icons** (`lucide-vue-next`).
* Configured global dark theme tokens in `src/style.css` (`#0D0D0D` background, `#161616` surface, `#00FF85` primary accent, and `#1E90FF` secondary/hover accent).
* Added TypeScript authentication and health-check contracts in `src/types/auth.ts`.
* Implemented HTTP client in `src/api/authService.ts` supporting `GET /health`, `POST /auth/login`, and `POST /auth/logout`.
* Added `FriendlyAuthError` translation layer with request timeouts, credential/network error mapping, and an active `/health` check to differentiate wrong credentials from an offline Python backend.
* Built isolated `LoginView.vue` with **Hisense** and **Midea / SmartHome** brand tabs, password visibility toggle, optional local IP input for Midea devices, and a borderless electric-blue (`#1E90FF`) brand icon.
* Added session bootstrap and logout handling in `src/App.vue` to persist active sessions across page reloads.