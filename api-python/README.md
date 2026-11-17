# Hisense ConnectLife Bridge API (`api-python`)

API ponte local desenvolvida em **Python + FastAPI** para comunicação com a nuvem **Hisense ConnectLife**. 

Este serviço atua como camada de integração rápida (Fase 1 e Fase 3 do monorepo `hisense-controller`), encapsulando a autenticação SSO (Gigya) e o protocolo de propriedades da Hisense por meio da biblioteca comunitária `connectlife`. Ele expõe endpoints REST simples em `localhost` para serem consumidos pela interface desktop em **Vue 3 / Tauri**, preparando o contrato que futuramente será migrado para o microsserviço definitivo em **Java 21** (`backend-java`).

---

## Pré-requisitos

* **Python 3.11+** instalado e configurado no `PATH`.
* **Conta ConnectLife** configurada com **e-mail e senha** (contas vinculadas exclusivamente via login social *Google/Apple* precisam definir uma senha pelo fluxo *"Esqueci minha senha"* no aplicativo antes de usar a API).
* Ar-condicionado Hisense pareado no aplicativo ConnectLife e conectado à rede Wi-Fi.

---

## 1. Configuração do Ambiente Virtual

Acesse a pasta `api-python`, crie o ambiente virtual isolado e instale as dependências do projeto:

```powershell
cd api-python
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn pydantic-settings connectlife
```

*(Caso o PowerShell bloqueie a ativação do script, execute `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` e rode o `Activate.ps1` novamente).*

---

## 2. Extração de Propriedades (Dump Inicial)

Antes de subir a API pela primeira vez, recomenda-se rodar o utilitário de dump em uma pasta ignorada pelo Git para validar suas credenciais e inspecionar o código do seu modelo (ex.: `008-301` para ar-condicionado de janela):

```powershell
mkdir dump
cd dump
python -m connectlife.dump --username "seu_email@dominio.com" --password 'sua_senha'
cd ..
```

O comando gerará um arquivo JSON (como `008-301.json`) contendo o bloco `statusList` com todas as chaves suportadas pelo aparelho.

> **Aviso de Segurança:** Nunca versione arquivos da pasta `dump/` nem compartilhe campos sensíveis como `puid`, `deviceId`, `mac` ou tokens de sessão.

---

## 3. Configuração das Variáveis de Ambiente

Crie o arquivo `.env` na raiz de `api-python` a partir do modelo `.env.example`:

```powershell
Copy-Item .env.example .env
```

Edite o `.env` com suas credenciais reais e as origens permitidas no CORS:

```env
CL_USER="seu_email@dominio.com"
CL_PASS="sua_senha_aqui"
APP_TITLE="Hisense ConnectLife Bridge"
CORS_ORIGINS=["http://localhost:5173","[http://127.0.0.1:5173](http://127.0.0.1:5173)","tauri://localhost"]
```

---

## 4. Executando o Servidor

Com o `.venv` ativo e dentro de `api-python/`, inicie o servidor Uvicorn:

```powershell
uvicorn main:app --reload
```

* **URL Base da API:** `http://127.0.0.1:8000`
* **Documentação Interativa (Swagger UI):** `http://127.0.0.1:8000/docs`

---

## 5. Endpoints Disponíveis e Exemplos (Insomnia / cURL)

### `GET /status`
Consulta a nuvem da Hisense e retorna o apelido do aparelho junto com o estado atual de todos os sensores (`f_*`) e parâmetros configuráveis (`t_*`).

**Requisição:**
```bash
curl -X GET [http://127.0.0.1:8000/status](http://127.0.0.1:8000/status)
```

**Resposta (`200 OK`):**
```json
{
  "name": "Ar condicionado de janela",
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
Envia um ou mais comandos de alteração de estado para o ar-condicionado. Você pode enviar apenas a chave que deseja modificar ou combinar múltiplas propriedades em uma única requisição.

**Exemplo 1 — Alterar temperatura alvo para 22 °C:**
```json
{
  "t_temp": 22
}
```

**Exemplo 2 — Ligar no modo Refrigerar a 20 °C com ventilação Baixa:**
```json
{
  "t_power": 1,
  "t_work_mode": 2,
  "t_temp": 20,
  "t_fan_speed": 2
}
```

**Exemplo 3 — Desligar o aparelho:**
```json
{
  "t_power": 0
}
```

**Resposta (`200 OK`):**
```json
{
  "ok": true,
  "sent": {
    "t_temp": 22
  }
}
```

---

## 6. Mapa de Propriedades do Modelo (`008-301`)

| Chave | Acesso | Descrição | Valores Principais |
| :--- | :--- | :--- | :--- |
| `t_power` | Leitura / Escrita | Estado de energia | `0` = Desligado, `1` = Ligado |
| `t_temp` | Leitura / Escrita | Temperatura alvo (°C) | `16` a `30` |
| `t_temp_type` | Leitura / Escrita | Unidade de temperatura | `0` = Celsius, `1` = Fahrenheit |
| `t_work_mode` | Leitura / Escrita | Modo de operação | `0` = Ventilar, `1` = Aquecer, `2` = Refrigerar, `3` = Desumidificar, `4` = Auto |
| `t_fan_speed` | Leitura / Escrita | Velocidade do ventilador | `0` = Auto, `2` = Baixa, `3` = Média, `4` = Alta |
| `t_sleep` | Leitura / Escrita | Modo Dormir (Sleep) | `0` = Desativado, `1` = Ativado |
| `f_temp_in` | Somente Leitura | Temperatura ambiente interna | Valor inteiro em °C (ex.: `"20"`) |
| `f_e_*` | Somente Leitura | Flags de diagnóstico e sensores | `0` = Operação normal |

---

## Estrutura de Arquivos

```text
api-python/
├── .venv/              # Ambiente virtual Python (ignorado pelo Git)
├── dump/               # Arquivos JSON brutos extraídos da nuvem (ignorado pelo Git)
├── .env                # Credenciais e configurações locais (ignorado pelo Git)
├── .env.example        # Modelo de variáveis de ambiente
├── config.py           # Carregamento e validação tipada via pydantic-settings
├── main.py             # Inicialização do FastAPI, ciclo de vida e rotas REST
├── requirements.txt    # Dependências fixadas do projeto
└── README.md           # Documentação do serviço
```