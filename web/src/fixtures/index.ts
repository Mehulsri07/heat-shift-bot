// LABELLED FIXTURES for building screens before the API is live. Enabled with VITE_FIXTURES=1.
// The hours are real Open-Meteo values for Jaipur on 2025-05-20; see the note inside the JSON.
// Nothing here is shown to a real user: a production build must leave VITE_FIXTURES unset.
import type { Plan, ReadyPlan, Site, SiteInput } from '../api';
import planJson from './plan-2025-05-20.json';

const SITE_ID = planJson.site_id;
const READY_AFTER_MS = 2500; // long enough to see the loading state

let site: Site | null = null;
const requestedAt = new Map<string, number>();
const voiceAt = new Map<string, number>();

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const fixtureApi = {
  async createSite(input: SiteInput): Promise<{ site_id: string }> {
    await wait(400);
    site = { ...input, site_id: SITE_ID, created_at: new Date().toISOString() };
    return { site_id: SITE_ID };
  },

  async getSite(): Promise<Site> {
    await wait(200);
    return (
      site ?? {
        site_id: SITE_ID,
        created_at: new Date().toISOString(),
        name: 'FIXTURE site',
        lat: 26.9124,
        lon: 75.7873,
        language: 'hi',
        shift_start: '07:00',
        shift_end: '18:00',
        direct_sun: false,
      }
    );
  },

  async requestPlan(_siteId: string, date: string): Promise<{ status: 'pending' | 'ready' }> {
    await wait(200);
    if (!requestedAt.has(date)) requestedAt.set(date, Date.now());
    return { status: 'pending' };
  },

  async getPlan(siteId: string, date: string): Promise<Plan> {
    await wait(200);
    const started = requestedAt.get(date) ?? 0;
    if (Date.now() - started < READY_AFTER_MS) return { status: 'pending', site_id: siteId, date };
    const { _fixture: _note, ...plan } = planJson;
    const voiceStarted = voiceAt.get(date);
    // There is no fixture audio file, so a requested voice note ends as failed.
    const audio_status = voiceStarted === undefined ? 'none' : Date.now() - voiceStarted < READY_AFTER_MS ? 'pending' : 'failed';
    return { ...(plan as unknown as ReadyPlan), site_id: siteId, date, audio_status };
  },

  async requestVoice(_siteId: string, date: string): Promise<{ audio_status: 'pending' | 'ready' }> {
    await wait(200);
    voiceAt.set(date, Date.now());
    return { audio_status: 'pending' };
  },
};
