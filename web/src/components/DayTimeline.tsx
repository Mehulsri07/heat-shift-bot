import type { CSSProperties } from 'react';
import type { Hour, StopWindow } from '../api';
import type { Strings } from '../copy';
import { hourLabel, isStopped } from './hours';

interface Props {
  t: Strings;
  hours: Hour[];
  stop: StopWindow | null;
  nowHour?: string;
}

/**
 * The whole shift as one strip: each hour is a block in its band's colour, with the stop-work hours bracketed.
 * The list below says the same thing in words, so this strip is hidden from screen readers.
 */
export function DayTimeline({ t, hours, stop, nowHour }: Props) {
  return (
    <div className="timeline">
      <div className="timeline-track" aria-hidden="true">
        {hours.map((hour, index) => (
          <div
            key={hour.hour}
            className="tl-hour-block"
            data-band={hour.band}
            data-stop={isStopped(hour.hour, stop) ? '' : undefined}
            data-now={hour.hour.slice(0, 2) === nowHour ? '' : undefined}
            style={{ '--i': index } as CSSProperties}
          >
            <span className="tl-bar" />
            <span className="tl-label">{hourLabel(hour.hour)}</span>
          </div>
        ))}
      </div>
      {stop && (
        <p className="timeline-legend">
          <span className="legend-swatch" aria-hidden="true" />
          {t.stop_legend}
        </p>
      )}
    </div>
  );
}
