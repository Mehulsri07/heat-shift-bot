import { useCallback, useEffect, useState } from 'react';
import { ApiError, getPlan, requestPlan, type ReadyPlan } from './api';

const POLL_MS = 2000;
const GIVE_UP_MS = 60_000;

export type PlanState =
  | { phase: 'loading' }
  // `voiceStalled` is set when the voice note is still pending after the give-up time, so the app can offer it again.
  | { phase: 'ready'; plan: ReadyPlan; voiceStalled: boolean }
  // `code` is an API error code, or `timeout` / `plan_failed` / `network`.
  | { phase: 'failed'; code: string };

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const errorCode = (err: unknown) => (err instanceof ApiError ? err.code : 'network');

/**
 * Ask the API for a plan and poll until it is ready, failed, or 60 seconds have passed.
 * Keeps polling a ready plan while its voice note is still being made.
 * `retry` starts over; `refresh` re-reads the plan (call it after requesting a voice note).
 */
export function usePlan(siteId: string, date: string) {
  const [state, setState] = useState<PlanState>({ phase: 'loading' });
  const [attempt, setAttempt] = useState(0);
  const [refreshes, setRefreshes] = useState(0);

  // biome-ignore lint/correctness/useExhaustiveDependencies: attempt and refreshes exist only to re-run this effect
  useEffect(() => {
    let cancelled = false;
    const startedAt = Date.now();

    (async () => {
      try {
        // A refresh keeps the plan for this date on screen; anything else shows loading.
        setState((prev) =>
          prev.phase === 'ready' && prev.plan.date === date ? { ...prev, voiceStalled: false } : { phase: 'loading' },
        );
        // Safe to repeat: the API reuses a plan that exists or is already being built.
        await requestPlan(siteId, date);
        while (!cancelled) {
          const plan = await getPlan(siteId, date);
          if (cancelled) return;
          if (plan.status === 'failed') return setState({ phase: 'failed', code: 'plan_failed' });
          if (plan.status === 'ready') {
            setState({ phase: 'ready', plan, voiceStalled: false });
            if (plan.audio_status !== 'pending') return;
          }
          if (Date.now() - startedAt > GIVE_UP_MS) {
            if (plan.status !== 'ready') setState({ phase: 'failed', code: 'timeout' });
            // A voice note that never arrives leaves the ready plan on screen, with its button offered again.
            else setState({ phase: 'ready', plan, voiceStalled: true });
            return;
          }
          await sleep(POLL_MS);
        }
      } catch (err) {
        if (!cancelled) setState({ phase: 'failed', code: errorCode(err) });
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [siteId, date, attempt, refreshes]);

  const retry = useCallback(() => {
    setState({ phase: 'loading' });
    setAttempt((n) => n + 1);
  }, []);
  const refresh = useCallback(() => setRefreshes((n) => n + 1), []);

  return { state, retry, refresh };
}

/** Today's date in Asia/Kolkata as YYYY-MM-DD, shifted by `offsetDays`. India has no daylight saving. */
export function istDate(offsetDays = 0): string {
  const ist = new Date(Date.now() + (5.5 + 24 * offsetDays) * 3_600_000);
  return ist.toISOString().slice(0, 10);
}
