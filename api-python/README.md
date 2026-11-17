# Hisense ConnectLife Bridge API (`api-python`)

Local bridge API built with **Python + FastAPI** for communication with the **Hisense ConnectLife** cloud. 

This service acts as a rapid integration layer (Phase 1 and Phase 3 of the `hisense-controller` monorepo), encapsulating Gigya SSO authentication and the Hisense properties protocol through the community `connectlife` library. It exposes simple REST endpoints on `localhost` to be consumed by the **Vue 3 / Tauri** desktop interface, establishing the contract that will later be migrated to the definitive **Java 21** microservice (`backend-java`).

---

## Prerequisites

* **Python 3.11+** installed and configured in your `PATH`.
* **ConnectLife Account** configured with an **email and password** (accounts exclusively linked via *Google/Apple* social login must set a password via the *"Forgot my password"* flow in the mobile app before using the API).
* Hisense air conditioner paired in the ConnectLife app and connected to the Wi-Fi network.

---

## 1. Virtual Environment Setup

Navigate to the `api-python` folder, create the isolated virtual environment, and install the project dependencies:

```powershell
cd api-python
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn pydantic-settings connectlife
```

*(If PowerShell blocks script activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and run `Activate.ps1` again).*

---

## 2. Property Extraction (Initial Dump)

Before starting the API for the first time, it is recommended to run the dump utility in a Git-ignored folder to validate your credentials and inspect your model's code (e.g., `008-301` for window air conditioners):

```powershell
mkdir dump
cd dump
python -m connectlife.dump --username "your_email@domain.com" --password 'your_password'
cd ..
```

The command will generate a JSON file (such as `008-301.json`) containing the `statusList` block with all keys supported by the device.

> **Security Warning:** Never version control files inside the `dump/` folder nor share sensitive fields like `puid`, `deviceId`, `mac`, or session tokens.

---

## 3. Environment Variables Configuration

Create the `.env` file in the root of `api-python` based on the `.env.example` template:

```powershell
Copy-Item .env.example .env
```

Edit `.env` with your actual credentials and allowed CORS origins:

```env
CL_USER="your_email@domain.com"
CL_PASS="your_password_here"
APP_TITLE="Hisense ConnectLife Bridge"
CORS_ORIGINS=["http://localhost:5173","[http://127.0.0.1:5173](http://127.0.0.1:5173)","tauri://localhost"]
```

---

## 4. Running the Server

With the `.venv` active and inside `api-python/`, start the Uvicorn server:

```powershell
uvicorn main:app --reload
```

* **Base API URL:** `http://127.0.0.1:8000`
* **Interactive Documentation (Swagger UI):** `http://127.0.0.1:8000/docs`

---

## 5. Available Endpoints and Examples (Insomnia / cURL)

### `GET /status`
Queries the Hisense cloud and returns the device nickname along with the current state of all sensors (`f_*`) and configurable parameters (`t_*`).

**Request:**
```bash
curl -X GET [http://127.0.0.1:8000/status](http://127.0.0.1:8000/status)
```

**Response (`200 OK`):**
```json
{
  "name": "Window Air Conditioner",
  "status": {
    "f_temp_in": "20",
    "t_power": "1",
    "t_temp": "20",
    "t_temp_type": "0",
    "t_work_mode": "2",
    "t_fan_speed": "2",
    "t_sleep": "0",
    "f_e_incoiltemp": "0",
    "f_e_incom": "0",
    "f_e_ineeprom": "0",
    "f_e_intemp": "0",
    "f_e_over_cold": "0",
    "f_e_over_hot": "0",
    "f_e_push": "0"
  }
}
```

---

### `POST /control`
Sends one or more state-change commands to the air conditioner. You can send only the key you want to modify or combine multiple properties into a single request.

**Example 1 — Change target temperature to 22 °C:**
```json
{
  "t_temp": 22
}
```

**Example 2 — Turn on in Cool mode at 20 °C with Low fan speed:**
```json
{
  "t_power": 1,
  "t_work_mode": 2,
  "t_temp": 20,
  "t_fan_speed": 2
}
```

**Example 3 — Turn off the device:**
```json
{
  "t_power": 0
}
```

**Response (`200 OK`):**
```json
{
  "ok": true,
  "sent": {
    "t_temp": 22
  }
}
```

---

## 6. Model Property Map (`008-301`)

| Key | Access | Description | Main Values |
| :--- | :--- | :--- | :--- |
| `t_power` | Read / Write | Power state | `0` = Off, `1` = On |
| `t_temp` | Read / Write | Target temperature (°C) | `16` to `30` |
| `t_temp_type` | Read / Write | Temperature unit | `0` = Celsius, `1` = Fahrenheit |
| `t_work_mode` | Read / Write | Operation mode | `0` = Fan, `1` = Heat, `2` = Cool, `3` = Dry, `4` = Auto |
| `t_fan_speed` | Read / Write | Fan speed | `0` = Auto, `2` = Low, `3` = Medium, `4` = High |
| `t_sleep` | Read / Write | Sleep mode | `0` = Disabled, `1` = Enabled |
| `f_temp_in` | Read-only | Indoor ambient temperature | Integer value in °C (e.g., `"20"`) |
| `f_e_*` | Read-only | Diagnostic flags and sensors | `0` = Normal operation |

---

## File Structure

```text
api-python/
├── .venv/              # Python virtual environment (Git-ignored)
├── dump/               # Raw JSON files extracted from the cloud (Git-ignored)
├── .env                # Local credentials and settings (Git-ignored)
├── .env.example        # Environment variables template
├── config.py           # Typed loading and validation via pydantic-settings
├── main.py             # FastAPI initialization, lifecycle, and REST routes
├── requirements.txt    # Pinned project dependencies
└── README.md           # Service documentation
```
