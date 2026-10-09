import { useEffect, useState } from 'react';
import { ApiError, getSite, type Site } from '../api';
import { fill, type Language, type Strings } from '../copy';
import { Segmented } from '../Segmented';
import { isNativeApp } from '../share';
import { istDate } from '../usePlan';
import { DayPlan } from './DayPlan';

interface Props {
  t: Strings;
  language: Language;
  onLanguage: (language: Language) => void;
  siteId: string;
  onChangeSite: () => void;
}

type Day = 'today' | 'tomorrow' | 'date';

/** The current hour in Asia/Kolkata as "HH". */
const istHour = () => new Date(Date.now() + 5.5 * 3_600_000).toISOString().slice(11, 13);

/** Re-read the clock every minute and when the app comes back to the front, so nothing on screen goes stale. */
function useIstHour(): string {
  const [hour, setHour] = useState(istHour);
  useEffect(() => {
    const tick = () => setHour(istHour());
    const timer = setInterval(tick, 60_000);
    document.addEventListener('visibilitychange', tick);
    return () => {
      clearInterval(timer);
      document.removeEventListener('visibilitychange', tick);
    };
  }, []);
  return hour;
}

/** How many columns the blank skeleton should show: one per shift hour. */
function shiftLength(site: Site | null): number {
  if (!site) return 11;
  const hours = Number(site.shift_end.slice(0, 2)) - Number(site.shift_start.slice(0, 2));
  return hours > 0 ? hours : 11;
}

export function Plan({ t, language, onLanguage, siteId, onChangeSite }: Props) {
  const [site, setSite] = useState<Site | null>(null);
  const [day, setDay] = useState<Day>('tomorrow');
  const [replayDate, setReplayDate] = useState('');
  const nowHour = useIstHour(); // also re-renders at midnight, so Today and Tomorrow move on
  const blanks = shiftLength(site);

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
      <header className="topbar">
        <div className="topbar-row">
          <div className="site">
            <h1 className="site-name">{site?.name ?? t.app_name}</h1>
            {site && (
              <p className="site-shift">{fill(t.site_shift, { start: site.shift_start, end: site.shift_end })}</p>
            )}
          </div>
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

      <main className="page">
        {/* Today and Tomorrow are both loaded up front, so switching never waits. */}
        <div hidden={day !== 'today'}>
          <DayPlan t={t} siteId={siteId} date={istDate(0)} nowHour={nowHour} blanks={blanks} />
        </div>
        <div hidden={day !== 'tomorrow'}>
          <DayPlan t={t} siteId={siteId} date={istDate(1)} blanks={blanks} />
        </div>
        {day === 'date' && (
          <>
            <section className="replay">
              <h2 className="replay-title">{t.replay_title}</h2>
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
              <p className="field-note">{t.replay_date_hint}</p>
            </section>
            {replayDate && <DayPlan key={replayDate} t={t} siteId={siteId} date={replayDate} blanks={blanks} />}
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
