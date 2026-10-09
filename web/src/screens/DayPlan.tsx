import type { ReadyPlan } from '../api';
import { Cooling } from '../components/Cooling';
import { Failed } from '../components/Failed';
import { Hero } from '../components/Hero';
import { HourList } from '../components/HourList';
import { Loading } from '../components/Loading';
import { RedFlag } from '../components/RedFlag';
import { VoiceNote } from '../components/VoiceNote';
import type { Strings } from '../copy';
import { usePlan } from '../usePlan';

interface Props {
  t: Strings;
  siteId: string;
  date: string;
  /** Set only for today: the hour to mark as current. */
  nowHour?: string;
  /** The number of blocks the loading skeleton shows: one per shift hour. */
  blanks: number;
}

/** One day's plan: loads it, then shows loading, failed or the plan. */
export function DayPlan({ t, siteId, date, nowHour, blanks }: Props) {
  const { state, retry, refresh } = usePlan(siteId, date);

  if (state.phase === 'loading') return <Loading t={t} blanks={blanks} />;
  if (state.phase === 'failed') return <Failed t={t} code={state.code} onRetry={retry} />;

  return (
    <PlanView
      t={t}
      siteId={siteId}
      plan={state.plan}
      voiceStalled={state.voiceStalled}
      nowHour={nowHour}
      onVoiceRequested={refresh}
    />
  );
}

interface ViewProps {
  t: Strings;
  siteId: string;
  plan: ReadyPlan;
  voiceStalled: boolean;
  nowHour?: string;
  onVoiceRequested: () => void;
}

// Everything below shows what the API returned. Nothing here decides a band, a time or a warning.
function PlanView({ t, siteId, plan, voiceStalled, nowHour, onVoiceRequested }: ViewProps) {
  return (
    <div className="plan">
      <Hero t={t} maxBand={plan.max_band} stop={plan.stop_window} hours={plan.hours} nowHour={nowHour} />

      {plan.red_flag && <RedFlag t={t} text={plan.red_flag} />}

      <HourList t={t} hours={plan.hours} stop={plan.stop_window} nowHour={nowHour} />

      <section className="card" aria-labelledby="plan-title">
        <h2 id="plan-title" className="card-title">
          {t.plan_heading}
        </h2>
        <p className="plan-text">{plan.plan_text}</p>
      </section>

      <Cooling t={t} points={plan.cooling_points} />

      <p className="source">
        {plan.source === 'replay' ? t.source_replay : t.source_forecast}, {plan.date}
      </p>

      <VoiceNote t={t} siteId={siteId} plan={plan} stalled={voiceStalled} onRequested={onVoiceRequested} />
    </div>
  );
}
