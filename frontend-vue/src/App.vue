<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { CheckCircle2, LogOut } from 'lucide-vue-next';
import { authService } from './api/authService';
import type { AuthDeviceResponse } from './types/auth';
import LoginView from './views/LoginView.vue';

const connectedDevice = ref<AuthDeviceResponse | null>(null);
const checkingSession = ref(true);

onMounted(async () => {
  try {
    const health = await authService.getHealth();
    if (health.hasSession && health.brand) {
      connectedDevice.value = {
        brand: health.brand,
        deviceName: 'Sessão ativa salva localmente',
        online: true,
      };
    }
  } catch {
    // Backend offline: mantém na tela de login
  } finally {
    checkingSession.value = false;
  }
});

async function handleLogout() {
  try {
    await authService.logout();
  } finally {
    connectedDevice.value = null;
  }
}
</script>

<template>
  <div v-if="checkingSession" class="center-screen">
    Verificando sessão...
  </div>

  <LoginView
      v-else-if="!connectedDevice"
      @authenticated="connectedDevice = $event"
  />

  <div v-else class="center-screen">
    <div class="session-card">
      <CheckCircle2 :size="30" class="success-icon" />
      <h2>{{ connectedDevice.deviceName }}</h2>
      <p>Fabricante: {{ connectedDevice.brand.toUpperCase() }}</p>
      <button class="logout-btn" @click="handleLogout">
        <LogOut :size="16" />
        <span>Sair e voltar ao login</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.center-screen {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  color: var(--muted);
}

.session-card {
  width: 100%;
  max-width: 380px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 28px 24px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.success-icon {
  color: var(--accent-1);
}

.session-card h2 {
  font-size: 1.1rem;
  color: var(--text);
}

.session-card p {
  font-size: 0.85rem;
}

.logout-btn {
  margin-top: 8px;
  background: var(--bg);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 9px 16px;
  border-radius: 9px;
  font-size: 0.84rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: border-color 0.15s ease, color 0.15s ease;
}

.logout-btn:hover {
  border-color: var(--accent-2);
  color: var(--accent-2);
}
</style>