import { useCallback, useEffect, useState } from 'react';
import { copy, type Language } from './copy';
import { Plan } from './screens/Plan';
import { Setup } from './screens/Setup';

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

export default function App() {
  const [language, setLanguage] = useState<Language>(() => (stored('language') === 'en' ? 'en' : 'hi'));
  const [siteId, setSiteId] = useState(() => stored('site_id'));
  const t = copy[language];

  useEffect(() => {
    remember('language', language);
    document.documentElement.lang = language;
    document.title = t.app_name;
  }, [language, t]);

  const saveSite = (id: string) => {
    remember('site_id', id);
    setSiteId(id);
  };
  const changeSite = useCallback(() => {
    remember('site_id', null);
    setSiteId(null);
  }, []);

  return (
    <div className="app">
      {siteId ? (
        <Plan t={t} language={language} onLanguage={setLanguage} siteId={siteId} onChangeSite={changeSite} />
      ) : (
        <Setup t={t} language={language} onLanguage={setLanguage} onSaved={saveSite} />
      )}
    </div>
  );
}
