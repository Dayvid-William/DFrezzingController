# DFrezzingController — Frontend

Desktop user interface for **DFrezzingController**, built with **Vue 3 + TypeScript + Vite** for local-first climate control of **Hisense** (ConnectLife) and **Midea / SmartHome** air conditioners.

---

## Tech Stack

* **Framework:** Vue 3 (`<script setup>` Single-File Components)
* **Language:** TypeScript
* **Bundler / Dev Server:** Vite
* **Icons:** `lucide-vue-next`
* **Styling:** Scoped CSS (`<style scoped>`) with global CSS custom properties (`src/style.css`)

---

## Design Tokens & Color Palette

The dark theme is defined in `src/style.css` to ensure high contrast and clear visual feedback:

| Token | Value | Purpose |
| :--- | :--- | :--- |
| `--bg` | `#0D0D0D` | Main window background and form inputs |
| `--surface` | `#161616` | Cards, containers, and active switcher tabs |
| `--text` | `#FFFFFF` | Primary headings and body text |
| `--muted` | `#A1A1AA` | Subtitles, field labels, and inactive controls |
| `--accent-1` | `#00FF85` | Primary call-to-action (CTA), active status, and selected brand tab |
| `--accent-2` | `#1E90FF` | Brand logo icon, input focus rings, links, and hover states |
| `--border` | `rgba(255, 255, 255, 0.10)` | Subtle borders for cards and form controls |

---

## Project Structure

```text
frontend-vue/
├── public/                 # Static public assets
├── src/
│   ├── api/
│   │   └── authService.ts  # HTTP client (fetch), timeouts, and user-friendly error mapping
│   ├── assets/             # Project media and static resources
│   ├── components/         # Reusable dashboard control widgets (upcoming)
│   ├── types/
│   │   └── auth.ts         # TypeScript interfaces for authentication and session state
│   ├── views/
│   │   └── LoginView.vue   # Multi-brand authentication screen (Hisense / Midea)
│   ├── App.vue             # Initial session check (/health) and view routing
│   ├── main.ts             # Vue application entry point
│   └── style.css           # Global CSS reset and design tokens
├── CHANGELOG.md
├── index.html
├── package.json
├── README.md
├── tsconfig.json
└── vite.config.ts
```

---

## Prerequisites & Configuration

1. **Node.js** (v18 or later recommended).
2. **Python Backend (FastAPI)** running locally on port `8000` (`http://127.0.0.1:8000`) with `CORSMiddleware` configured to allow `http://localhost:5173`.

### Environment Variables (Optional)

By default, the HTTP client targets `http://127.0.0.1:8000`. To override the backend URL, create a `.env` file in the `frontend-vue` root directory:

```env
VITE_API_URL=[http://127.0.0.1:8000](http://127.0.0.1:8000)
```

---

## Getting Started

Run the following commands inside the `frontend-vue` directory:

```powershell
# Install dependencies
npm install

# Start the development server (http://localhost:5173)
npm run dev

# Type-check and build for production
npm run build

# Preview the production build locally
npm run preview
```

---

## Implemented Features

* **Multi-Brand Authentication:** Brand switcher supporting **Hisense** (ConnectLife) and **Midea / SmartHome** with brand-specific helper hints.
* **Manual Local IP Override (Midea):** Expandable field to manually specify the air conditioner's local Wi-Fi IP address.
* **Session Persistence:** Automatic session check via `GET /health` on startup, restoring saved local sessions seamlessly.
* **User-Friendly Error Handling:** Translates raw driver/HTTP errors (`401`, cloud codes `3101` and `3102`, request timeouts, and local Wi-Fi socket errors) into clear UI alerts, using a `/health` probe to distinguish invalid credentials from an offline backend service.