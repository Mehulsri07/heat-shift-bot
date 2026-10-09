import { useEffect, useState, type CSSProperties } from 'react';
import { ApiError, getSite, requestVoice, type ReadyPlan, type Site } from '../api';
import { errorText, fill, type Language, type Strings } from '../copy';
import { Segmented } from '../Segmented';
import { isNativeApp, shareVoiceNote } from '../share';
import { istDate, usePlan } from '../usePlan';

interface Props {
  t: Strings;
  language: Language;
  onLanguage: (language: Language) => void;
  siteId: string;
  onChangeSite: () => void;
}

type Day = 'today' | 'tomorrow' | 'date';

export function Plan({ t, language, onLanguage, siteId, onChangeSite }: Props) {
  const [site, setSite] = useState<Site | null>(null);
  const [day, setDay] = useState<Day>('tomorrow');
  const [replayDate, setReplayDate] = useState('');

  useEffect(() => {
    let live = true;
    getSite(siteId)
      .then((found) => live && setSite(found))
      .catch((err) => {
        // A site the API no longer knows cannot show a plan: go back to setup.
        if (live && err instanceof ApiError && err.code === 'site_not_found') onChangeSite();
      });
    return () => {
      live = false;
    };
  }, [siteId, onChangeSite]);

  return (
    <>
      <header className="shell">
        <div className="shell-bar">
          <h1 className="shell-title">{site?.name ?? t.app_name}</h1>
          <Segmented
            quiet
            variant="compact"
            name="language"
            legend={t.language_label}
            value={language}
            onChange={onLanguage}
            options={[
              { value: 'hi', label: t.lang_hi },
              { value: 'en', label: t.lang_en },
            ]}
          />
        </div>
        <Segmented
          quiet
          variant="tabs"
          name="day"
          legend={t.day_tabs_label}
          value={day}
          onChange={setDay}
          options={[
            { value: 'today', label: t.tab_today },
            { value: 'tomorrow', label: t.tab_tomorrow },
            { value: 'date', label: t.tab_date },
          ]}
        />
      </header>

      <main className="page page-flush">
        {/* Today and Tomorrow are both loaded up front, so switching never waits. */}
        <div hidden={day !== 'today'}>
          <DayPlan t={t} siteId={siteId} date={istDate(0)} isToday />
        </div>
        <div hidden={day !== 'tomorrow'}>
          <DayPlan t={t} siteId={siteId} date={istDate(1)} />
        </div>
        {day === 'date' && (
          <>
            <div className="replay">
              <label className="field-label" htmlFor="replay-date">
                {t.replay_date_label}
              </label>
              <input
                id="replay-date"
                className="input input-figure"
                type="date"
                max={istDate(-1)}
                value={replayDate}
                onChange={(e) => setReplayDate(e.target.value)}
              />
              {!replayDate && <p className="field-note">{t.replay_date_hint}</p>}
            </div>
            {replayDate && <DayPlan key={replayDate} t={t} siteId={siteId} date={replayDate} />}
          </>
        )}
      </main>

      <footer className="foot">
        <button type="button" className="button-link" onClick={onChangeSite}>
          {t.change_site}
        </button>
        {!isNativeApp && (
          <a className="button-link" href="/download/app.apk">
            {t.download_app}
          </a>
        )}
      </footer>
    </>
  );
}

interface DayProps {
  t: Strings;
  siteId: string;
  date: string;
  isToday?: boolean;
}

function DayPlan({ t, siteId, date, isToday }: DayProps) {
  const { state, retry, refresh } = usePlan(siteId, date);

  if (state.phase === 'loading') {
    return (
      <div className="state" role="status">
        <p className="state-title">{t.loading_plan}</p>
        <p className="state-note">{t.loading_hint}</p>
        <div className="roller" aria-hidden="true" />
        <ol className="strip strip-blank" aria-hidden="true">
          {Array.from({ length: 8 }, (_, index) => (
            <li key={index} className="chip">
              <span className="chip-rail" />
              <span className="chip-field" />
            </li>
          ))}
        </ol>
      </div>
    );
  }

  if (state.phase === 'failed') {
    return (
      <div className="state" role="alert">
        <p className="state-title">{errorText(t, state.code)}</p>
        <button type="button" className="button button-quiet" onClick={retry}>
          {t.retry}
        </button>
      </div>
    );
  }

  return <ReadyPlanView t={t} siteId={siteId} plan={state.plan} isToday={isToday} onVoiceRequested={refresh} />;
}

/** The current hour in Asia/Kolkata as "HH", used only to mark today's current row. */
const istHour = () => new Date(Date.now() + 5.5 * 3_600_000).toISOString().slice(11, 13);

interface ReadyProps {
  t: Strings;
  siteId: string;
  plan: ReadyPlan;
  isToday?: boolean;
  onVoiceRequested: () => void;
}

// Everything below shows what the API returned. Nothing here decides a band, a time or a warning.
function ReadyPlanView({ t, siteId, plan, isToday, onVoiceRequested }: ReadyProps) {
  const stop = plan.stop_window;
  const nowHour = isToday ? istHour() : null;
  const bandName = t as unknown as Record<string, string>;

  return (
    <>
      <section className="summary" data-stop={stop ? '' : undefined}>
        {stop ? (
          <h2 className="summary-head">
            <span className="summary-label">{t.stop_window_label}</span>{' '}
            <span className="summary-times">{fill(t.stop_window_times, stop)}</span>
          </h2>
        ) : (
          <h2 className="summary-none">{t.no_stop_window}</h2>
        )}
      </section>

      <h2 className="visually-hidden">{t.hours_heading}</h2>
      <ol className="strip">
        {plan.hours.map((hour, index) => {
          const stopped = stop !== null && hour.hour >= stop.start && hour.hour < stop.end;
          const current = hour.hour.slice(0, 2) === nowHour;
          return (
            <li
              key={hour.hour}
              className="chip"
              data-band={hour.band}
              data-stop={stopped ? '' : undefined}
              data-now={current ? '' : undefined}
              style={{ '--i': index } as CSSProperties}
            >
              <span className="chip-rail" aria-hidden="true" />
              <span className="chip-field" aria-hidden="true" />
              <span className="chip-hour">{hour.hour}</span>
              <span className="chip-name">
                {bandName[`band_${hour.band}`] ?? hour.band}
                {stopped && <span className="visually-hidden">, {t.stop_mark}</span>}
              </span>
              <span className="chip-temp">{fill(t.temp, { t: hour.temp_c })}</span>
              {current && <span className="chip-now">{t.now}</span>}
            </li>
          );
        })}
      </ol>

      <section className="block">
        <h2 className="block-title">{t.plan_heading}</h2>
        <p className="plan-text">{plan.plan_text}</p>
      </section>

      {plan.red_flag && (
        <section className="redflag">
          <h2 className="redflag-title">{t.red_flag_heading}</h2>
          <p className="redflag-text">{plan.red_flag}</p>
        </section>
      )}

      <VoiceNote t={t} siteId={siteId} plan={plan} onRequested={onVoiceRequested} />

      {plan.cooling_points.length > 0 && (
        <section className="block">
          <h2 className="block-title">{t.cooling_heading}</h2>
          <ul className="points">
            {plan.cooling_points.map((point) => (
              <li key={`${point.name}-${point.lat}-${point.lon}`} className="point">
                <span className="point-name">{point.name}</span>
                <span className="point-distance">{fill(t.distance_km, { km: point.distance_km })}</span>
                <span className="point-type">{bandName[`cooling_${point.type}`] ?? point.type}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <p className="source">
        {plan.source === 'replay' ? t.source_replay : t.source_forecast}, {plan.date}
      </p>
    </>
  );
}

interface VoiceProps {
  t: Strings;
  siteId: string;
  plan: ReadyPlan;
  onRequested: () => void;
}

function VoiceNote({ t, siteId, plan, onRequested }: VoiceProps) {
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
  const pending = asking || plan.audio_status === 'pending';

  return (
    <section className="block">
      <h2 className="block-title">{t.voice_heading}</h2>
      {url ? (
        <>
          <audio className="player" controls preload="none" src={url} />
          <button
            type="button"
            className="button"
            onClick={async () => setNeedsLink(!(await shareVoiceNote(url, t.voice_share_title)))}
          >
            {t.voice_share}
          </button>
          {needsLink && (
            <a className="button-link" href={url} target="_blank" rel="noopener">
              {t.voice_open}
            </a>
          )}
        </>
      ) : (
        <>
          <p className="block-note">{t.voice_hint}</p>
          {plan.audio_status === 'failed' && !pending && (
            <p className="notice" role="alert">
              {t.voice_failed}
            </p>
          )}
          {error && (
            <p className="notice" role="alert">
              {error}
            </p>
          )}
          <button type="button" className="button" onClick={make} disabled={pending}>
            {pending ? t.voice_pending : plan.audio_status === 'failed' ? t.retry : t.voice_make}
          </button>
        </>
      )}
    </section>
  );
}
