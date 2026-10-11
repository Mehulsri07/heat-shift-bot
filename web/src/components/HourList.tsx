import type { Hour, StopWindow } from '../api';
import { bandText, fill, type Strings } from '../copy';
import { isStopped } from './hours';

interface Props {
  t: Strings;
  hours: Hour[];
  stop: StopWindow | null;
  nowHour?: string;
}

/** Every hour in words: the time, the band name, the temperature and the heat index. Screen readers use this. */
export function HourList({ t, hours, stop, nowHour }: Props) {
  return (
    <section className="card" aria-labelledby="hours-title">
      <h2 id="hours-title" className="card-title">
        {t.hours_heading}
      </h2>
      <p className="card-note">{t.hours_note}</p>
      <ol className="hour-list">
        {hours.map((hour) => {
          const stopped = isStopped(hour.hour, stop);
          const current = hour.hour.slice(0, 2) === nowHour;
          return (
            <li
              key={hour.hour}
              className="hour-row"
              data-stop={stopped ? '' : undefined}
              data-now={current ? '' : undefined}
            >
              <span className="hour-time-cell">
                <span className="hour-time">{hour.hour}</span>
                {stopped && <span className="hour-stop">{t.stop_mark}</span>}
                {current && <span className="hour-now">{t.now}</span>}
              </span>
              <span className="band-chip hour-band" data-band={hour.band}>
                {bandText(t, hour.band)}
              </span>
              <span className="hour-temp">{fill(t.temp, { t: hour.temp_c })}</span>
              <span className="hour-hi">{fill(t.heat_index, { hi: hour.heat_index_c })}</span>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
