import { type CSSProperties, useEffect, useState } from 'react';
import type { Strings } from '../copy';

interface Props {
  t: Strings;
  blanks: number;
}

const STEP_MS = 2600;

/**
 * The plan is still being built. The skeleton has the shape of the real plan, and the three steps tell the
 * supervisor what is happening while the wait lasts.
 */
export function Loading({ t, blanks }: Props) {
  const steps = [t.loading_step_1, t.loading_step_2, t.loading_step_3];
  const [step, setStep] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setStep((current) => (current + 1) % steps.length), STEP_MS);
    return () => clearInterval(timer);
  }, [steps.length]);

  return (
    <div className="loading" role="status">
      <div className="loading-head">
        <p className="loading-title">{t.loading_title}</p>
        <p className="loading-step" key={step}>
          {steps[step]}
        </p>
        <p className="loading-hint">{t.loading_hint}</p>
      </div>
      <div className="skeleton-hero" aria-hidden="true" />
      <div className="skeleton-columns" aria-hidden="true">
        {Array.from({ length: blanks }, (_, index) => (
          // biome-ignore lint/suspicious/noArrayIndexKey: identical placeholders that never reorder
          <span key={index} className="skeleton-column" style={{ '--i': index } as CSSProperties} />
        ))}
      </div>
    </div>
  );
}
