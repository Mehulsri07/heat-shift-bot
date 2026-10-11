import type { CoolingPoint } from '../api';
import { fill, type Strings } from '../copy';

interface Props {
  t: Strings;
  points: CoolingPoint[];
}

/** Nearby places to cool down, in the order the API sent them: nearest first. */
export function Cooling({ t, points }: Props) {
  if (points.length === 0) return null;
  const label = t as unknown as Record<string, string>;
  return (
    <section aria-labelledby="cooling-title">
      <h2 id="cooling-title" className="card-title cooling-heading">
        {t.cooling_heading}
      </h2>
      <ul className="cooling">
        {points.map((point) => (
          <li key={`${point.name}-${point.lat}-${point.lon}`} className="cooling-card" data-type={point.type}>
            <span className="cooling-type">{label[`cooling_${point.type}`] ?? point.type}</span>
            <span className="cooling-name">{point.name}</span>
            <span className="cooling-distance">{fill(t.distance_km, { km: point.distance_km })}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
