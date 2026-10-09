import { type FormEvent, useEffect, useState } from 'react';
import { Geolocation } from '@capacitor/geolocation';
import { ApiError, createSite } from '../api';
import { errorText, fill, type Language, type Strings } from '../copy';
import { Segmented } from '../Segmented';

interface Props {
  t: Strings;
  language: Language;
  onLanguage: (language: Language) => void;
  onSaved: (siteId: string) => void;
  /** Set when a site already exists: step 1 can then go back to the plan. */
  onBack: (() => void) | null;
}

type Locating = 'idle' | 'busy' | 'found' | 'denied';
const STEPS = 3;

/** Latitude and longitude as typed. An empty or out-of-range value is not a location yet. */
const inRange = (value: string, limit: number) => value.trim() !== '' && Math.abs(Number(value)) <= limit;

export function Setup({ t, language, onLanguage, onSaved, onBack }: Props) {
  // Each step is a history entry, so the browser or phone back button moves between steps.
  const [step, setStep] = useState<number>(() => history.state?.wizardStep ?? 0);
  useEffect(() => {
    const onPop = (event: PopStateEvent) => {
      if (event.state?.view === 'setup') setStep(event.state.wizardStep ?? 0);
    };
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);
  const goStep = (next: number) => {
    history.pushState({ view: 'setup', wizardStep: next }, '');
    setStep(next);
  };
  const [name, setName] = useState('');
  const [lat, setLat] = useState('');
  const [lon, setLon] = useState('');
  const [shiftStart, setShiftStart] = useState('07:00');
  const [shiftEnd, setShiftEnd] = useState('18:00');
  const [directSun, setDirectSun] = useState<'yes' | 'no' | null>(null);
  const [locating, setLocating] = useState<Locating>('idle');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const valid = [
    name.trim().length >= 1 && name.trim().length <= 60,
    inRange(lat, 90) && inRange(lon, 180),
    directSun !== null && shiftStart < shiftEnd,
  ];
  const isLast = step === STEPS - 1;

  async function useMyLocation() {
    setLocating('busy');
    try {
      const { coords } = await Geolocation.getCurrentPosition({ enableHighAccuracy: true, timeout: 15000 });
      setLat(coords.latitude.toFixed(5));
      setLon(coords.longitude.toFixed(5));
      setLocating('found');
    } catch {
      setLocating('denied');
    }
  }

  async function save() {
    setSaving(true);
    setError(null);
    try {
      const { site_id } = await createSite({
        name: name.trim(),
        lat: Number(lat),
        lon: Number(lon),
        language,
        shift_start: shiftStart,
        shift_end: shiftEnd,
        direct_sun: directSun === 'yes',
      });
      onSaved(site_id);
    } catch (err) {
      setError(errorText(t, err instanceof ApiError ? err.code : 'network'));
      setSaving(false);
    }
  }

  function next(event: FormEvent) {
    event.preventDefault();
    if (!valid[step]) return;
    if (isLast) void save();
    else goStep(step + 1);
  }

  return (
    <>
      <header className="topbar">
        <div className="topbar-row">
          <p className="brand">{t.app_name}</p>
        </div>
        <div
          className="progress"
          role="progressbar"
          aria-label={fill(t.step_of, { current: step + 1, total: STEPS })}
          aria-valuemin={1}
          aria-valuemax={STEPS}
          aria-valuenow={step + 1}
        >
          <span className="progress-fill" style={{ width: `${((step + 1) / STEPS) * 100}%` }} />
        </div>
      </header>

      <main className="page setup">
        <form className="wizard" onSubmit={next} noValidate>
          <p className="step-count">{fill(t.step_of, { current: step + 1, total: STEPS })}</p>

          {step === 0 && (
            <section className="wizard-step" aria-labelledby="setup-title">
              <h1 id="setup-title" className="setup-title">
                {t.setup_site_title}
              </h1>
              <p className="lede">{t.setup_site_intro}</p>
              <div className="field">
                <label className="field-label" htmlFor="site-name">
                  {t.site_name_label}
                </label>
                <input
                  id="site-name"
                  className="input input-large"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder={t.site_name_placeholder}
                  maxLength={60}
                  autoComplete="off"
                />
              </div>
              <Segmented
                name="setup-language"
                legend={t.setup_language_label}
                value={language}
                onChange={onLanguage}
                options={[
                  { value: 'hi', label: t.lang_hi },
                  { value: 'en', label: t.lang_en },
                ]}
              />
            </section>
          )}

          {step === 1 && (
            <section className="wizard-step" aria-labelledby="location-title">
              <h1 id="location-title" className="setup-title">
                {t.setup_location_title}
              </h1>
              <p className="lede">{t.setup_location_intro}</p>
              <button
                type="button"
                className="button button-quiet button-locate"
                onClick={useMyLocation}
                disabled={locating === 'busy'}
                data-locating={locating === 'busy' ? '' : undefined}
              >
                {locating === 'busy' ? t.locating : t.use_location}
              </button>
              <p className="field-note" role="status">
                {locating === 'found' && t.location_found}
                {locating === 'denied' && t.location_denied}
              </p>
              <details className="manual" open={locating === 'denied'}>
                <summary>{t.manual_location}</summary>
                <div className="pair">
                  <div>
                    <label className="field-sublabel" htmlFor="lat">
                      {t.lat_label}
                    </label>
                    <input
                      id="lat"
                      className="input input-figure"
                      type="number"
                      inputMode="decimal"
                      step="any"
                      min={-90}
                      max={90}
                      value={lat}
                      onChange={(e) => setLat(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="field-sublabel" htmlFor="lon">
                      {t.lon_label}
                    </label>
                    <input
                      id="lon"
                      className="input input-figure"
                      type="number"
                      inputMode="decimal"
                      step="any"
                      min={-180}
                      max={180}
                      value={lon}
                      onChange={(e) => setLon(e.target.value)}
                    />
                  </div>
                </div>
              </details>
            </section>
          )}

          {step === 2 && (
            <section className="wizard-step" aria-labelledby="shift-title">
              <h1 id="shift-title" className="setup-title">
                {t.setup_shift_title}
              </h1>
              <p className="lede">{t.setup_shift_intro}</p>
              <div className="field pair">
                <div>
                  <label className="field-label" htmlFor="shift-start">
                    {t.shift_start}
                  </label>
                  <input
                    id="shift-start"
                    className="input input-figure"
                    type="time"
                    value={shiftStart}
                    onChange={(e) => setShiftStart(e.target.value)}
                  />
                </div>
                <div>
                  <label className="field-label" htmlFor="shift-end">
                    {t.shift_end}
                  </label>
                  <input
                    id="shift-end"
                    className="input input-figure"
                    type="time"
                    value={shiftEnd}
                    onChange={(e) => setShiftEnd(e.target.value)}
                  />
                </div>
              </div>

              <fieldset className="field">
                <legend className="field-label">{t.direct_sun_label}</legend>
                <div className="choices">
                  <label className="choice" data-selected={directSun === 'yes' ? '' : undefined}>
                    <input type="radio" name="direct-sun" value="yes" checked={directSun === 'yes'} onChange={() => setDirectSun('yes')} />
                    <span className="choice-title">{t.direct_sun_yes}</span>
                    <span className="choice-hint">{t.direct_sun_yes_hint}</span>
                  </label>
                  <label className="choice" data-selected={directSun === 'no' ? '' : undefined}>
                    <input type="radio" name="direct-sun" value="no" checked={directSun === 'no'} onChange={() => setDirectSun('no')} />
                    <span className="choice-title">{t.direct_sun_no}</span>
                    <span className="choice-hint">{t.direct_sun_no_hint}</span>
                  </label>
                </div>
              </fieldset>
            </section>
          )}

          {error && (
            <p className="notice" role="alert">
              {error}
            </p>
          )}

          <div className="wizard-actions">
            {(step > 0 || onBack) && (
              <button
                type="button"
                className="button button-quiet"
                onClick={() => (step > 0 ? goStep(step - 1) : onBack?.())}
              >
                {t.back}
              </button>
            )}
            <button type="submit" className="button" disabled={!valid[step] || saving}>
              {isLast ? (saving ? t.saving : t.save_site) : t.next}
            </button>
          </div>
        </form>
      </main>
    </>
  );
}
