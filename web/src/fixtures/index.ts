// LABELLED FIXTURES for building screens before the API is live. Enabled with VITE_FIXTURES=1.
// The hours are real Open-Meteo values for Jaipur on 2025-05-20; see the note inside each JSON.
// Nothing here is shown to a real user: a production build must leave VITE_FIXTURES unset.
//
// Add ?fixture=<mode> to the address to see one state:
//   sun     the direct-sun variant (reaches EXTREME_DANGER)
//   voice   the voice note is already made
//   failed  the plan failed
//   slow    the plan never arrives (the loading state)
//   stuck   the plan is ready but its voice note never arrives (the stalled-voice state)
import type { Plan, ReadyPlan, Site, SiteInput } from '../api';
import sunJson from './plan-2025-05-20-direct-sun.json';
import planJson from './plan-2025-05-20.json';

const SITE_ID = planJson.site_id;
const READY_AFTER_MS = 2500; // long enough to see the loading state
const mode = new URLSearchParams(location.search).get('fixture');

let site: Site | null = null;
const requestedAt = new Map<string, number>();
const voiceAt = new Map<string, number>();

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

/** One second of silence, so the player and share button have something to hold. */
let silence: string | null = null;
function silentAudioUrl(): string {
  if (silence) return silence;
  const samples = 8000;
  const wav = new Uint8Array(44 + samples).fill(0x80, 44);
  const view = new DataView(wav.buffer);
  const text = (offset: number, value: string) => {
    for (let i = 0; i < value.length; i++) view.setUint8(offset + i, value.charCodeAt(i));
  };
  text(0, 'RIFF');
  view.setUint32(4, 36 + samples, true);
  text(8, 'WAVEfmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true); // PCM
  view.setUint16(22, 1, true); // mono
  view.setUint32(24, 8000, true);
  view.setUint32(28, 8000, true);
  view.setUint16(32, 1, true);
  view.setUint16(34, 8, true);
  text(36, 'data');
  view.setUint32(40, samples, true);
  silence = URL.createObjectURL(new Blob([wav], { type: 'audio/wav' }));
  return silence;
}

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
    if (mode === 'slow' || Date.now() - started < READY_AFTER_MS) return { status: 'pending', site_id: siteId, date };
    if (mode === 'failed') return { status: 'failed', site_id: siteId, date };

    const { _fixture: _note, ...plan } = mode === 'sun' || site?.direct_sun ? sunJson : planJson;
    const voiceStarted = mode === 'voice' ? 0 : voiceAt.get(date);
    const audio_status =
      voiceStarted === undefined
        ? 'none'
        : mode === 'stuck' || Date.now() - voiceStarted < READY_AFTER_MS
          ? 'pending'
          : 'ready';
    return {
      ...(plan as unknown as ReadyPlan),
      site_id: siteId,
      date,
      audio_status,
      audio_url: audio_status === 'ready' ? silentAudioUrl() : null,
    };
  },

  async requestVoice(_siteId: string, date: string): Promise<{ audio_status: 'pending' | 'ready' }> {
    await wait(200);
    voiceAt.set(date, Date.now());
    return { audio_status: 'pending' };
  },
};
