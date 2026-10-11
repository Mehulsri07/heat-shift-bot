import { type CSSProperties, useState } from 'react';
import { ApiError, requestVoice, type ReadyPlan } from '../api';
import { errorText, type Strings } from '../copy';
import { shareVoiceNote } from '../share';

interface Props {
  t: Strings;
  siteId: string;
  plan: ReadyPlan;
  /** The note has been pending past the give-up time: offer the button again instead of waiting forever. */
  stalled: boolean;
  onRequested: () => void;
}

// One bar per 70 ms of delay; the delay is unique, so it doubles as the key.
const WAVE_DELAYS = Array.from({ length: 16 }, (_, index) => index * 70);

/** The crew voice note, docked to the bottom of the plan: make it, play it, share it. */
export function VoiceNote({ t, siteId, plan, stalled, onRequested }: Props) {
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [needsLink, setNeedsLink] = useState(false);

  async function make() {
    setAsking(true);
    setError(null);
    try {
      await requestVoice(siteId, plan.date);
      onRequested();
    } catch (err) {
      setError(errorText(t, err instanceof ApiError ? err.code : 'network'));
    } finally {
      setAsking(false);
    }
  }

  const url = plan.audio_status === 'ready' ? plan.audio_url : null;
  const pending = asking || (plan.audio_status === 'pending' && !stalled);
  const failed = plan.audio_status === 'failed' || stalled;
  const state = url ? 'ready' : pending ? 'pending' : failed ? 'failed' : 'idle';

  return (
    <div className="dock" data-state={state}>
      <section className="dock-card" aria-labelledby="voice-title">
        <div className="dock-head">
          <h2 id="voice-title" className="dock-title">
            {t.voice_heading}
          </h2>
          {url && <span className="dock-pill">{t.voice_ready}</span>}
        </div>

        {url ? (
          <>
            {/* biome-ignore lint/a11y/useMediaCaption: the plan text on this screen is what the voice note says */}
            <audio className="player" controls preload="none" src={url} />
            <button
              type="button"
              className="button"
              onClick={async () => setNeedsLink(!(await shareVoiceNote(url, t.voice_share_title)))}
            >
              {t.voice_share}
            </button>
            {needsLink && (
              <a className="voice-link" href={url} target="_blank" rel="noopener">
                {t.voice_open}
              </a>
            )}
          </>
        ) : pending ? (
          <>
            <div className="wave" aria-hidden="true">
              {WAVE_DELAYS.map((delay, index) => (
                <span key={delay} className="wave-bar" style={{ '--i': index } as CSSProperties} />
              ))}
            </div>
            <p className="dock-status" role="status">
              {t.voice_pending}
            </p>
          </>
        ) : (
          <>
            <p className="dock-hint">{t.voice_hint}</p>
            {failed && (
              <p className="notice" role="alert">
                {stalled ? t.voice_stalled : t.voice_failed}
              </p>
            )}
            {error && (
              <p className="notice" role="alert">
                {error}
              </p>
            )}
            <button type="button" className="button" onClick={make}>
              {failed ? t.retry : t.voice_make}
            </button>
          </>
        )}
      </section>
    </div>
  );
}
