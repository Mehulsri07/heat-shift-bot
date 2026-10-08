import en from './copy/en.json';
import hi from './copy/hi.json';

// Every UI string comes from the copy files, keyed by name, in both languages.
export const copy = { en, hi };
export type Language = keyof typeof copy;

export default function App() {
  const t = copy.hi;
  return (
    <main>
      <h1>{t.app_name}</h1>
    </main>
  );
}
