# DFrezzingController

Fullscreen desktop application for Windows (`.exe`) designed for unified control of **Hisense** and **Midea** air conditioners (including *Split Inverter* models such as the Midea Xtreme Save and ConnectLife window units).

The project follows a **Local-First** architecture built around the **Adapter** pattern: a Python backend runs locally as a *sidecar* (`127.0.0.1`) bundled inside a **Tauri v2** executable, translating proprietary manufacturer protocols into a standardized REST contract consumed by a **Vue 3** interface.

---

## Key Features

* **Decoupled Multi-Brand Support:** Single interface capable of operating **Hisense** units (via ConnectLife cloud) and **Midea** units (via MSmartHome + local M-Smart V3 network), dynamically adapting visible controls based on each model's capabilities (e.g., louver swing).
* **Offline LAN Control (Midea):** After initial online pairing to extract V3 cryptographic keys (`token` and `key`), all IP discovery (UDP broadcast on ports `6445`/`20086`) and command execution (TCP on port `6444`) run 100% on the local network without internet access, including automatic recovery if the router reassigns the unit's IP via DHCP.
* **Zero-Config Session Persistence:** Saves pairing state to `%APPDATA%/ac-controller/session.json`, skipping the login screen on subsequent application launches.
* **Lightweight Windows Packaging:** Uses native WebView2 via Tauri v2 with managed child-process lifecycle handling to prevent orphan background processes when closing the window.
* **Hybrid-Ready Contract:** The HTTP API is designed so a remote server can be plugged in later as the primary endpoint with automatic `localhost` failover.

---

## Tech Stack

| Layer | Directory | Technologies | Responsibility |
| :--- | :--- | :--- | :--- |
| **Backend Sidecar** | `api-python/` | Python 3.12, FastAPI, Uvicorn, `connectlife`, `msmart-ng`, PyInstaller | Multi-brand drivers (`BaseAcAdapter`), session persistence, and local REST API. |
| **Frontend UI** | `frontend-vue/` | Vue 3, TypeScript, Vite, Tailwind CSS | Responsive fullscreen dashboard, pairing screen, and optimistic state sync. |
| **Desktop Shell** | `src-tauri/` | Tauri v2 (Rust) | Free port allocation, sidecar lifecycle management, and `.exe` bundling. |
| **Future Evolution** | `backend-java/` | Java 21, Spring Boot / Quarkus | Reserved workspace for future remote microservice migration. |
| **Documentation** | `docs/` | Markdown | Architectural planning (`PLAN.md`) and protocol mappings. |

---

## Monorepo Structure

```text
DFrezzingController/
├── api-python/             # Multi-brand bridge backend (Hisense + Midea)
│   ├── adapters/           # Isolated manufacturer drivers (base, hisense, midea)
│   ├── dump/               # Raw device property dumps (ignored by Git)
│   ├── config.py           # Settings and CORS configuration via pydantic-settings
│   ├── main.py             # FastAPI routes and application lifespan
│   ├── schemas.py          # Normalized Pydantic models (AcStatus, AcCommand)
│   ├── session.py          # Session manager stored in %APPDATA%
│   └── requirements.txt    # Pinned Python dependencies
├── frontend-vue/           # Fullscreen desktop UI (Vue 3 + TS + Tailwind)
├── backend-java/           # Reserved directory for future Java implementation
├── docs/                   # Technical documentation and architecture plan (PLAN.md)
└── README.md               # General project documentation
```

---

## Standardized HTTP Contract

All manufacturer drivers map proprietary payloads to the same endpoints exposed on `http://127.0.0.1:<PORT>`:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Checks sidecar availability and reports whether an active session exists (`hasSession`). |
| `POST` | `/auth/login` | Authenticates with the selected brand's cloud (`hisense` or `midea`), extracts keys/PUID, discovers local IP, and writes `session.json`. |
| `POST` | `/auth/logout` | Deletes the local session file to allow switching devices or manufacturers. |
| `GET` | `/ac/status` | Returns the normalized state (`power`, `targetTemp`, `ambientTemp`, `mode`, `fanSpeed`, `swing`). |
| `POST` | `/ac/command` | Accepts partial state updates and applies them to the active air conditioner. |

---

## Running in Development

### Prerequisites
* **Python 3.12+**
* **Node.js 20+** and **npm**
* Email and password configured on **ConnectLife** (Hisense) or **MSmartHome** (Midea), with the air conditioner already paired to the local Wi-Fi network.

### 1. Start the Backend (`api-python`)
```powershell
cd api-python
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```
* **Local API:** `http://127.0.0.1:8000`
* **Swagger UI:** `http://127.0.0.1:8000/docs`

### 2. Start the Frontend (`frontend-vue`)
In a second terminal:
```powershell
cd frontend-vue
npm install
npm run dev
```
* **Web UI (Dev):** `http://localhost:5173`
