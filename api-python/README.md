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
