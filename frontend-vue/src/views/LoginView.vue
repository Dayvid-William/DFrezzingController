<script setup lang="ts">
import { computed, ref } from 'vue';
import {
  Snowflake,
  Wifi,
  AlertCircle,
  Eye,
  EyeOff,
  Loader2,
} from 'lucide-vue-next';
import { authService, FriendlyAuthError } from '../api/authService';
import type { AuthDeviceResponse, Brand } from '../types/auth';

const emit = defineEmits<{
  authenticated: [device: AuthDeviceResponse];
}>();

const brand = ref<Brand>('hisense');
const email = ref('');
const password = ref('');
const ip = ref('');
const showPassword = ref(false);
const showAdvanced = ref(false);
const isLoading = ref(false);
const errorState = ref<{ title: string; message: string } | null>(null);

const brandHint = computed(() =>
    brand.value === 'hisense'
        ? 'Use as credenciais da sua conta ConnectLife.'
        : 'Use as credenciais da conta SmartHome (mesma rede Wi-Fi do aparelho).'
);

function selectBrand(selected: Brand) {
  brand.value = selected;
  errorState.value = null;
}

async function handleSubmit() {
  isLoading.value = true;
  errorState.value = null;

  try {
    const device = await authService.login({
      brand: brand.value,
      email: email.value.trim(),
      password: password.value,
      ...(brand.value === 'midea' && ip.value.trim() ? { ip: ip.value.trim() } : {}),
    });
    emit('authenticated', device);
  } catch (err) {
    if (err instanceof FriendlyAuthError) {
      errorState.value = { title: err.title, message: err.message };
    } else {
      errorState.value = {
        title: 'Falha ao conectar',
        message: 'Não foi possível concluir o login. Tente novamente.',
      };
    }
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="auth-wrapper">
    <form class="auth-card" @submit.prevent="handleSubmit">
      <header class="auth-header">
        <div class="logo-badge">
          <Snowflake :size="26" />
        </div>
        <h1>DFrezzingController</h1>
        <p>Conecte seu ar-condicionado para iniciar</p>
      </header>

      <div class="brand-switcher" role="tablist" aria-label="Fabricante">
        <button
            type="button"
            role="tab"
            :aria-selected="brand === 'hisense'"
            :class="['brand-tab', { active: brand === 'hisense' }]"
            @click="selectBrand('hisense')"
        >
          Hisense
        </button>
        <button
            type="button"
            role="tab"
            :aria-selected="brand === 'midea'"
            :class="['brand-tab', { active: brand === 'midea' }]"
            @click="selectBrand('midea')"
        >
          Midea / SmartHome
        </button>
      </div>

      <p class="brand-hint">{{ brandHint }}</p>

      <div class="form-group">
        <label for="email">E-mail</label>
        <input
            id="email"
            v-model="email"
            type="email"
            autocomplete="email"
            required
            placeholder="seu@email.com"
        />
      </div>

      <div class="form-group">
        <label for="password">Senha</label>
        <div class="password-field">
          <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="current-password"
              required
              placeholder="••••••••"
          />
          <button
              type="button"
              class="toggle-pass-btn"
              :title="showPassword ? 'Ocultar senha' : 'Mostrar senha'"
              @click="showPassword = !showPassword"
          >
            <EyeOff v-if="showPassword" :size="17" />
            <Eye v-else :size="17" />
          </button>
        </div>
      </div>

      <div v-if="brand === 'midea'" class="advanced-section">
        <button
            type="button"
            class="advanced-toggle"
            @click="showAdvanced = !showAdvanced"
        >
          <Wifi :size="14" />
          <span>
            {{ showAdvanced ? 'Ocultar IP manual' : 'Informar IP local manualmente (opcional)' }}
          </span>
        </button>

        <div v-if="showAdvanced" class="form-group">
          <label for="device-ip">IP do aparelho na rede Wi-Fi</label>
          <input
              id="device-ip"
              v-model="ip"
              type="text"
              placeholder="Ex.: 192.168.1.15"
          />
        </div>
      </div>

      <div v-if="errorState" class="error-box" role="alert">
        <AlertCircle :size="18" class="error-icon" />
        <div class="error-content">
          <strong class="error-title">{{ errorState.title }}</strong>
          <p class="error-message">{{ errorState.message }}</p>
        </div>
      </div>

      <button type="submit" class="submit-btn" :disabled="isLoading">
        <Loader2 v-if="isLoading" :size="18" class="spin" />
        <span>{{ isLoading ? 'Conectando...' : 'Conectar aparelho' }}</span>
      </button>
    </form>
  </div>
</template>

<style scoped>
.auth-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 28px 24px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.auth-header {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.logo-badge {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(30, 144, 255, 0.14);
  border: none;
  color: var(--accent-2);
  display: grid;
  place-items: center;
  margin-bottom: 4px;
}

.auth-header h1 {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text);
}

.auth-header p {
  font-size: 0.84rem;
  color: var(--muted);
}

.brand-switcher {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  background: var(--bg);
  border: 1px solid var(--border);
  padding: 4px;
  border-radius: 10px;
}

.brand-tab {
  background: transparent;
  border: none;
  color: var(--muted);
  font-size: 0.84rem;
  font-weight: 600;
  padding: 9px 10px;
  border-radius: 7px;
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.brand-tab:hover:not(.active) {
  color: var(--accent-2);
}

.brand-tab.active {
  background: var(--surface);
  color: var(--accent-1);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.45);
}

.brand-hint {
  font-size: 0.78rem;
  color: var(--muted);
  line-height: 1.4;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--muted);
}

.form-group input {
  width: 100%;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 9px;
  padding: 10px 12px;
  font-size: 0.9rem;
  color: var(--text);
  outline: none;
  transition: border-color 0.15s ease;
}

.form-group input::placeholder {
  color: #52525B;
}

.form-group input:focus {
  border-color: var(--accent-2);
}

.password-field {
  position: relative;
  display: flex;
  align-items: center;
}

.password-field input {
  padding-right: 40px;
}

.toggle-pass-btn {
  position: absolute;
  right: 10px;
  background: transparent;
  border: none;
  color: var(--muted);
  display: grid;
  place-items: center;
  cursor: pointer;
  padding: 4px;
  transition: color 0.15s ease;
}

.toggle-pass-btn:hover {
  color: var(--accent-2);
}

.advanced-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.advanced-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: none;
  color: var(--accent-2);
  font-size: 0.8rem;
  cursor: pointer;
  padding: 0;
  width: fit-content;
}

.advanced-toggle:hover {
  text-decoration: underline;
}

.error-box {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: rgba(239, 68, 68, 0.10);
  border: 1px solid rgba(239, 68, 68, 0.35);
  padding: 11px 12px;
  border-radius: 10px;
}

.error-icon {
  flex-shrink: 0;
  margin-top: 2px;
  color: #F87171;
}

.error-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.error-title {
  font-size: 0.84rem;
  font-weight: 700;
  color: #FCA5A5;
}

.error-message {
  font-size: 0.79rem;
  color: #FECACA;
  line-height: 1.4;
}

.submit-btn {
  margin-top: 4px;
  background: var(--accent-1);
  color: #05140C;
  border: none;
  border-radius: 10px;
  padding: 11px 16px;
  font-size: 0.92rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background-color 0.15s ease, color 0.15s ease, transform 0.1s ease;
}

.submit-btn:hover:not(:disabled) {
  background: var(--accent-2);
  color: #FFFFFF;
}

.submit-btn:active:not(:disabled) {
  transform: scale(0.99);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>