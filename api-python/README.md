# Multi-Brand AC Bridge API (`api-python`)

Local bridge and sidecar API built with **Python + FastAPI** for unified control of **Hisense** and **Midea** air conditioners.

This service acts as the backend layer of the application (packaged into the Tauri v2 desktop shell or runnable standalone). It normalizes proprietary vendor protocols (Hisense ConnectLife cloud and Midea M-Smart V3 local LAN protocol) into a single, standardized REST contract consumed by the frontend.

---

## Prerequisites by Manufacturer

### General
* **Python 3.11+** installed and available in your system `PATH`.

### Hisense Air Conditioners
* **ConnectLife Account** with a configured email and password.
  * *Note:* Accounts created exclusively via Google/Apple social login must set a password using the *"Forgot my password"* option in the ConnectLife mobile app before using the API.
* Air conditioner paired in the ConnectLife mobile app and connected to the Wi-Fi network.

### Midea Air Conditioners
* **MSmartHome** or **NetHome Plus** account with configured email and password.
* Air conditioner paired in the official mobile app and connected to the **same local network subnet** as this computer.
* **Network / Router Requirements:**
  * **Same Subnet:** The PC and the Midea AC must be on the same Wi-Fi / LAN network (e.g., both on `192.168.1.x`).
  * **AP / Client Isolation:** Must be **disabled** in your Wi-Fi router settings (otherwise devices cannot communicate with each other).
  * **UDP Broadcast:** Allowed on ports `6445` and `20086` for automatic device discovery.
  * **TCP Local Port:** Port `6444` open on the local network for command dispatch and telemetry.

---

## 1. Setup and Installation

Navigate to the `api-python` directory, create a virtual environment, and install dependencies:

```powershell
cd api-python
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

*(If PowerShell restricts execution of the activation script, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in the current terminal session).*

---

## 2. Manufacturer Inspection and Diagnostic Tools

Before running the API, you can use the built-in diagnostic tools to verify connectivity with your appliances.

### Hisense: Cloud Property Dump (`connectlife`)
Extract raw property dictionaries and identify your model code (e.g., `008-301`):

```powershell
mkdir dump
cd dump
python -m connectlife.dump --username "your_email@domain.com" --password 'your_password'
cd ..
```

This generates a JSON file (e.g., `008-301.json`) containing the full property map (`statusList`).

> **Security Note:** Files in `dump/` contain private device identifiers and are ignored by Git. Never commit or share them.

### Midea: Local LAN Discovery and Capabilities (`msmart-ng`)
You can discover and inspect Midea appliances on your local network using the bundled `msmart-ng` CLI:

**1. Discover devices on the local network (UDP broadcast):**
```powershell
python -m msmart.cli discover
```

**2. Discover and automatically authenticate using cloud credentials:**
```powershell
python -m msmart.cli discover --account "your_email@domain.com" --password "your_password"
```

**3. Query device capabilities (louver angles, modes, sensors) by local IP:**
```powershell
python -m msmart.cli query <DEVICE_IP> --auto --account "your_email@domain.com" --password "your_password" --capabilities
```

---

## 3. Configuration & Session Persistence

### Environment Variables (`.env`)
Copy the template to create a local `.env`:

```powershell
Copy-Item .env.example .env
```

```env
CL_USER=""
CL_PASS=""
APP_TITLE="DFrezzingController API"
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173","tauri://localhost"]
```

### Zero-Config Session Storage
When authenticating via `POST /auth/login`, the application saves credentials and cryptographic keys to:
* **Windows:** `%APPDATA%\ac-controller\session.json`
* **Linux/macOS:** `~/.ac-controller/session.json`

On subsequent launches, the API automatically restores connection without prompting for credentials.

---

## 4. Running the API

Start the Uvicorn development server:

```powershell
uvicorn main:app --reload
```

* **Base URL:** `http://127.0.0.1:8000`
* **Interactive Documentation (Swagger UI):** `http://127.0.0.1:8000/docs`
* **Alternative OpenAPI Docs (ReDoc):** `http://127.0.0.1:8000/redoc`

---

## 5. Normalized REST Endpoints

All endpoints use normalized domain models, decoupling the frontend from brand-specific protocols.

### `GET /health`
Verifies API status and whether an active session is already loaded.

**Response (`200 OK`):**
```json
{
  "status": "ok",
  "mode": "local",
  "hasSession": true
}
```

---

### `POST /auth/login`
Authenticates with the chosen brand, pairs the appliance, and saves the session.

#### Example: Hisense
```json
{
  "brand": "hisense",
  "email": "user@domain.com",
  "password": "hisense_password"
}
```

#### Example: Midea
```json
{
  "brand": "midea",
  "email": "user@domain.com",
  "password": "midea_password"
}
```

**Response (`200 OK`):**
```json
{
  "ok": true,
  "brand": "midea",
  "deviceName": "Living Room AC"
}
```

---

### `POST /auth/logout`
Clears the active session and deletes the local `session.json` file.

**Response (`200 OK`):**
```json
{
  "ok": true
}
```

---

### `GET /ac/status`
Queries current device state and returns normalized properties.

**Response (`200 OK`):**
```json
{
  "brand": "midea",
  "deviceName": "Living Room AC",
  "power": true,
  "targetTemp": 22,
  "ambientTemp": 24,
  "mode": "cool",
  "fanSpeed": "auto",
  "swing": "off"
}
```

---

### `POST /ac/command`
Applies partial state updates to the active air conditioner. Send only the fields you want to change.

**Example 1 — Set temperature to 20 °C:**
```json
{
  "targetTemp": 20
}
```

**Example 2 — Turn on, set to Cool mode, 22 °C, medium fan:**
```json
{
  "power": true,
  "mode": "cool",
  "targetTemp": 22,
  "fanSpeed": "medium"
}
```

**Example 3 — Turn off:**
```json
{
  "power": false
}
```

**Response (`200 OK`):**
Returns the updated `AcStatus` object.

---

## 6. Supported Domain Values

| Parameter | Type / Values | Notes |
| :--- | :--- | :--- |
| `brand` | `"hisense"`, `"midea"` | Supported manufacturer integrations |
| `power` | `true`, `false` | Power state |
| `targetTemp` | `16` to `30` (°C) | Target temperature |
| `ambientTemp` | Integer (°C) or `null` | Current room temperature reported by sensors |
| `mode` | `"auto"`, `"cool"`, `"dry"`, `"heat"`, `"fan"` | Normalized operation modes |
| `fanSpeed` | `"auto"`, `"low"`, `"medium"`, `"high"` | Normalized fan speeds |
| `swing` | `"off"`, `"vertical"` | Louver movement state |

---

## 7. Architecture & Code Structure

```text
api-python/
├── adapters/
│   ├── baseAdapter.py      # Abstract BaseAcAdapter[T] generic contract
│   ├── hisenseAdapter.py   # ConnectLife cloud driver
│   └── mideaAdapter.py     # M-Smart V3 local LAN driver with DHCP recovery
├── config/
│   ├── config.py           # Settings and CORS configuration via pydantic-settings
│   └── session.py          # SessionManager handling %APPDATA%/ac-controller/session.json
├── enums/
│   ├── domainEnums.py      # Normalized domain enums (Brand, WorkMode, FanSpeed, SwingMode)
│   ├── hisenseEnums.py     # Vendor property codes and maps for Hisense
│   └── mideaEnums.py       # Constants for Midea LAN protocol (port 6444, device type 0xAC)
├── mappers/
│   ├── hisenseMapper.py    # Bidirectional translation (Domain <-> ConnectLife payload)
│   └── mideaMapper.py      # Bidirectional translation (Domain <-> MSmart device properties)
├── schemas/
│   ├── ac.py               # Normalized Pydantic models (AcStatus, AcCommand, LoginRequest)
│   └── session.py          # Discriminated session models (HisenseSession, MideaSession)
├── dump/                   # Property dumps for device research (Git-ignored)
├── main.py                 # FastAPI application, lifecycle, and endpoint definitions
├── pyproject.toml          # PEP 621 package metadata and dependency specification
├── requirements.txt        # Pinned requirements list
└── README.md               # API documentation
```
