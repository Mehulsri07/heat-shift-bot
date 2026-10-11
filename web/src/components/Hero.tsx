import type { Band, Hour, StopWindow } from '../api';
import { bandText, fill, type Strings } from '../copy';
import { DayTimeline } from './DayTimeline';

interface Props {
  t: Strings;
  /** The highest band of the day, from the API. It sets the colour of the whole card. */
  maxBand: Band;
  stop: StopWindow | null;
  hours: Hour[];
  nowHour?: string;
}

// The card takes the tint of the day's highest band. The colour only says what the API decided.
export function Hero({ t, maxBand, stop, hours, nowHour }: Props) {
  return (
    <section className="hero" data-band={maxBand} aria-labelledby="hero-title">
      <span className="band-chip" data-band={maxBand}>
        <span className="hero-level-label">{t.hero_level_label}</span>
        <strong>{bandText(t, maxBand)}</strong>
      </span>

      {stop ? (
        <>
          <h2 id="hero-title" className="hero-title">
            {t.hero_stop_label}
          </h2>
          <p className="hero-times">{fill(t.hero_stop_times, { start: stop.start, end: stop.end })}</p>
        </>
      ) : (
        <h2 id="hero-title" className="hero-title hero-title-quiet">
          {t.hero_no_stop}
        </h2>
      )}

      <div className="hero-glance">
        <p className="hero-glance-title">{t.day_at_a_glance}</p>
        <DayTimeline t={t} hours={hours} stop={stop} nowHour={nowHour} />
      </div>
    </section>
  );
}
