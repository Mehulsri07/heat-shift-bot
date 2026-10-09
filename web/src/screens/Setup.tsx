import { useState, type FormEvent } from 'react';
import { Geolocation } from '@capacitor/geolocation';
import { ApiError, createSite } from '../api';
import { errorText, type Language, type Strings } from '../copy';
import { Segmented } from '../Segmented';

interface Props {
  t: Strings;
  language: Language;
  onLanguage: (language: Language) => void;
  onSaved: (siteId: string) => void;
}

type Locating = 'idle' | 'busy' | 'found' | 'denied';

export function Setup({ t, language, onLanguage, onSaved }: Props) {
  const [name, setName] = useState('');
  const [lat, setLat] = useState('');
  const [lon, setLon] = useState('');
  const [shiftStart, setShiftStart] = useState('07:00');
  const [shiftEnd, setShiftEnd] = useState('18:00');
  const [directSun, setDirectSun] = useState<'yes' | 'no' | null>(null);
  const [locating, setLocating] = useState<Locating>('idle');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  async function save(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const { site_id } = await createSite({
        name,
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

  return (
    <>
      <header className="shell">
        <div className="shell-bar">
          <p className="shell-title">{t.app_name}</p>
        </div>
      </header>

      <main className="page">
        <h1 className="page-title">{t.setup_title}</h1>
        <p className="lede">{t.setup_intro}</p>

        <form className="form" onSubmit={save}>
          <Segmented
            name="language"
            legend={t.language_label}
            value={language}
            onChange={onLanguage}
            options={[
              { value: 'hi', label: t.lang_hi },
              { value: 'en', label: t.lang_en },
            ]}
          />

          <div className="field">
            <label className="field-label" htmlFor="site-name">
              {t.site_name_label}
            </label>
            <input
              id="site-name"
              className="input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={t.site_name_placeholder}
              maxLength={60}
              required
              autoComplete="off"
            />
          </div>

          <fieldset className="field">
            <legend className="field-label">{t.location_label}</legend>
            <button type="button" className="button button-quiet" onClick={useMyLocation} disabled={locating === 'busy'}>
              {locating === 'busy' ? t.locating : t.use_location}
            </button>
            <p className="field-note" role="status">
              {locating === 'found' && t.location_found}
              {locating === 'denied' && t.location_denied}
            </p>
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
                  required
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
                  required
                />
              </div>
            </div>
          </fieldset>

          <fieldset className="field">
            <legend className="field-label">{t.shift_label}</legend>
            <div className="pair">
              <div>
                <label className="field-sublabel" htmlFor="shift-start">
                  {t.shift_start}
                </label>
                <input
                  id="shift-start"
                  className="input input-figure"
                  type="time"
                  value={shiftStart}
                  onChange={(e) => setShiftStart(e.target.value)}
                  required
                />
              </div>
              <div>
                <label className="field-sublabel" htmlFor="shift-end">
                  {t.shift_end}
                </label>
                <input
                  id="shift-end"
                  className="input input-figure"
                  type="time"
                  value={shiftEnd}
                  onChange={(e) => setShiftEnd(e.target.value)}
                  required
                />
              </div>
            </div>
          </fieldset>

          <Segmented
            name="direct-sun"
            legend={t.direct_sun_label}
            value={directSun}
            onChange={setDirectSun}
            options={[
              { value: 'yes', label: t.yes },
              { value: 'no', label: t.no },
            ]}
          />

          {error && (
            <p className="notice" role="alert">
              {error}
            </p>
          )}

          <button type="submit" className="button" disabled={saving}>
            {saving ? t.saving : t.save_site}
          </button>
        </form>
      </main>
    </>
  );
}
