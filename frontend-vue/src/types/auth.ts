export type Brand = 'hisense' | 'midea'; //criar enum e importa

export interface LoginPayload {
    brand: Brand;
    email: string;
    password: string;
    ip?: string;
}

export interface AuthDeviceResponse {
    brand: Brand;
    deviceName: string;
    online: boolean;
}

export interface HealthResponse {
    status: 'ok';
    hasSession: boolean;
    brand?: Brand | null;
}