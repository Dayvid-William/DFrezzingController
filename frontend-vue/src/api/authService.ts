import type {
    AuthDeviceResponse,
    HealthResponse,
    LoginPayload,
} from '../types/auth';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

export class FriendlyAuthError extends Error {
    title: string;

    constructor(title: string, message: string) {
        super(message);
        this.name = 'FriendlyAuthError';
        this.title = title;
    }
}

function mapBackendError(status: number, rawDetail: string): FriendlyAuthError {
    const detail = rawDetail.toLowerCase();

    // Conta inexistente na nuvem (ex.: erro 3102 da Midea)
    if (
        detail.includes('3102') ||
        detail.includes('does not exist') ||
        detail.includes('not found')
    ) {
        return new FriendlyAuthError(
            'Conta não encontrada',
            'Não localizamos esse e-mail no fabricante selecionado. Confira a grafia ou alterne entre Hisense e Midea.'
        );
    }

    // E-mail ou senha incorretos (401, erro 3101 ou falha de login no driver)
    if (
        status === 401 ||
        detail.includes('3101') ||
        detail.includes('password') ||
        detail.includes('credential') ||
        detail.includes('unauthorized') ||
        detail.includes('invalid login') ||
        detail.includes('auth')
    ) {
        return new FriendlyAuthError(
            'E-mail ou senha incorretos',
            'Não foi possível validar seu acesso. Confira suas credenciais e tente novamente.'
        );
    }

    // Falha de comunicação local com a placa Wi-Fi (porta 6444, VPN ou aparelho offline)
    if (
        status === 502 ||
        status === 504 ||
        detail.includes('packet') ||
        detail.includes('discover') ||
        detail.includes('socket') ||
        detail.includes('6444') ||
        detail.includes('timed out')
    ) {
        return new FriendlyAuthError(
            'Aparelho não respondeu na rede',
            'Verifique se o ar-condicionado está na mesma rede Wi-Fi, desative VPNs no computador e feche o app SmartHome no celular.'
        );
    }

    // Erro de validação de campos (422)
    if (status === 422) {
        return new FriendlyAuthError(
            'Dados inválidos',
            'Verifique se o e-mail e o endereço IP (caso informado) foram preenchidos corretamente.'
        );
    }

    return new FriendlyAuthError(
        'Falha na conexão',
        'Não foi possível autenticar no fabricante. Confira suas credenciais e tente novamente.'
    );
}

async function isBackendAlive(): Promise<boolean> {
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 1500);
    try {
        const res = await fetch(`${BASE_URL}/health`, { signal: controller.signal });
        return res.ok;
    } catch {
        return false;
    } finally {
        clearTimeout(timer);
    }
}

async function request<T>(
    path: string,
    options?: RequestInit,
    timeoutMs = 15000
): Promise<T> {
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), timeoutMs);

    let response: Response;

    try {
        response = await fetch(`${BASE_URL}${path}`, {
            headers: { 'Content-Type': 'application/json' },
            signal: controller.signal,
            ...options,
        });
    } catch (err) {
        if (err instanceof DOMException && err.name === 'AbortError') {
            throw new FriendlyAuthError(
                'Tempo limite excedido',
                'A conexão demorou muito para responder. Verifique sua rede Wi-Fi e tente novamente.'
            );
        }

        if (path !== '/health' && (await isBackendAlive())) {
            throw new FriendlyAuthError(
                'E-mail ou senha incorretos',
                'O fabricante recusou o login. Confira suas credenciais e tente novamente.'
            );
        }

        throw new FriendlyAuthError(
            'Serviço local indisponível',
            'Não foi possível conectar ao motor do aplicativo (porta 8000). Verifique se o backend Python está em execução.'
        );
    } finally {
        clearTimeout(timer);
    }

    if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        const rawDetail =
            typeof errorBody?.detail === 'string'
                ? errorBody.detail
                : typeof errorBody?.message === 'string'
                    ? errorBody.message
                    : JSON.stringify(errorBody ?? '');

        throw mapBackendError(response.status, rawDetail);
    }

    if (response.status === 204) {
        return undefined as T;
    }

    return response.json() as Promise<T>;
}

export const authService = {
    getHealth: () => request<HealthResponse>('/health', undefined, 3000),

    login: (payload: LoginPayload) =>
        request<AuthDeviceResponse>(
            '/auth/login',
            {
                method: 'POST',
                body: JSON.stringify(payload),
            },
            20000
        ),

    logout: () =>
        request<void>('/auth/logout', {
            method: 'POST',
        }),
};