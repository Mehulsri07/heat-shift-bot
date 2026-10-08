// The API contract from PLAN.md, in TypeScript. Change the brief first, then this file.

const BASE: string = import.meta.env.VITE_API_BASE ?? '';

export type Band = 'SAFE' | 'CAUTION' | 'EXTREME_CAUTION' | 'DANGER' | 'EXTREME_DANGER';
export type AudioStatus = 'none' | 'pending' | 'ready' | 'failed';

export interface SiteInput {
  name: string;
  lat: number;
  lon: number;
  language: 'hi' | 'en';
  shift_start: string; // HH:MM
  shift_end: string; // HH:MM
  direct_sun: boolean;
}

export interface Site extends SiteInput {
  site_id: string;
  created_at: string;
}

export interface Hour {
  hour: string; // HH:MM
  temp_c: number;
  rh: number;
  heat_index_c: number;
  band: Band;
}

export interface CoolingPoint {
  name: string;
  type: 'water' | 'shade' | 'clinic';
  lat: number;
  lon: number;
  distance_km: number;
}

export interface ReadyPlan {
  status: 'ready';
  site_id: string;
  date: string; // YYYY-MM-DD
  source: 'forecast' | 'replay';
  hours: Hour[];
  stop_window: { start: string; end: string } | null;
  max_band: Band;
  plan_text: string;
  red_flag: string | null; // fixed text: show it word for word
  cooling_points: CoolingPoint[];
  audio_status: AudioStatus;
  audio_url: string | null; // valid for one hour
}

export type Plan = ReadyPlan | { status: 'pending' | 'failed'; site_id: string; date: string };

/** `code` is the API's error code; look up its sentence in the copy files. */
export class ApiError extends Error {
  status: number;
  code: string;

  constructor(status: number, code: string) {
    super(code);
    this.status = status;
    this.code = code;
  }
}

async function call<T>(method: 'GET' | 'POST', path: string, body?: unknown): Promise<T> {
  const response = await fetch(BASE + path, {
    method,
    headers: body === undefined ? undefined : { 'content-type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    // Throttling is answered by API Gateway itself, in its own shape.
    const fallback = response.status === 429 ? 'rate_limited' : 'server_error';
    throw new ApiError(response.status, data?.error ?? fallback);
  }
  return data as T;
}

export const createSite = (site: SiteInput) => call<{ site_id: string }>('POST', '/api/sites', site);

export const getSite = (siteId: string) => call<Site>('GET', `/api/sites/${siteId}`);

export const requestPlan = (siteId: string, date: string) =>
  call<{ status: 'pending' | 'ready' }>('POST', `/api/sites/${siteId}/plans`, { date });

export const getPlan = (siteId: string, date: string) =>
  call<Plan>('GET', `/api/sites/${siteId}/plans/${date}`);

export const requestVoice = (siteId: string, date: string) =>
  call<{ audio_status: 'pending' | 'ready' }>('POST', `/api/sites/${siteId}/plans/${date}/voice`);
