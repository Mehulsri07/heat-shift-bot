import { useCallback, useEffect, useState } from 'react';
import { copy, type Language } from './copy';
import { FIXTURE_BANNER } from './fixtures/banner';
import { Plan } from './screens/Plan';
import { Setup } from './screens/Setup';

type View = 'setup' | 'plan';
const isView = (value: unknown): value is View => value === 'setup' || value === 'plan';

// The app remembers two things on the phone: the language and the one site. There is no login.
const stored = (key: string) => {
  try {
    return localStorage.getItem(key);
  } catch {
    return null; // storage can be blocked in private browsing
  }
};
const remember = (key: string, value: string | null) => {
  try {
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, value);
  } catch {
    // nothing to do: the app still works for this visit
  }
};

/** Run a change of screen as a view transition where the browser has one; otherwise just run it. */
const withTransition = (change: () => void) => {
  if (typeof document.startViewTransition === 'function') document.startViewTransition(change);
  else change();
};

export default function App() {
  const [language, setLanguage] = useState<Language>(() => (stored('language') === 'en' ? 'en' : 'hi'));
  const [siteId, setSiteId] = useState(() => stored('site_id'));
  const [view, setView] = useState<View>(() => (stored('site_id') ? 'plan' : 'setup'));
  const t = copy[language];

  useEffect(() => {
    remember('language', language);
    document.documentElement.lang = language;
    document.title = t.app_name;
  }, [language, t]);

  // Every screen is a history entry, so the browser or phone back button goes back a screen.
  useEffect(() => {
    if (history.state?.view !== view) history.replaceState({ view }, '');
  }, [view]);

  useEffect(() => {
    const onPop = (event: PopStateEvent) => {
      const next = event.state?.view;
      if (isView(next)) withTransition(() => setView(next));
    };
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  const go = useCallback((next: View) => {
    history.pushState({ view: next }, '');
    withTransition(() => setView(next));
  }, []);

  const saveSite = useCallback(
    (id: string) => {
      remember('site_id', id);
      setSiteId(id);
      go('plan');
    },
    [go],
  );

  const changeSite = useCallback(() => go('setup'), [go]);

  return (
    <div className="app">
      {import.meta.env.VITE_FIXTURES === '1' && <p className="fixture-banner">{FIXTURE_BANNER}</p>}
      {view === 'plan' && siteId ? (
        <Plan t={t} language={language} onLanguage={setLanguage} siteId={siteId} onChangeSite={changeSite} />
      ) : (
        <Setup
          t={t}
          language={language}
          onLanguage={setLanguage}
          onSaved={saveSite}
          onBack={siteId ? () => go('plan') : null}
        />
      )}
    </div>
  );
}
