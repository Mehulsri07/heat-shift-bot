import en from './en.json';
import hi from './hi.json';

// Every UI string comes from these two files, keyed by name, in both languages.
export const copy = { en, hi };
export type Language = keyof typeof copy;
export type Strings = typeof en;

/** Fill `{name}` slots in a copy string. Values are shown exactly as given. */
export const fill = (template: string, values: Record<string, string | number>) =>
  template.replace(/\{(\w+)\}/g, (_, key: string) => String(values[key]));

/** The sentence for an API error code, falling back to the generic one. */
export const errorText = (t: Strings, code: string) =>
  (t as Record<string, string>)[`error_${code}`] ?? t.error_server_error;

/** The printed name of a band, so no band is ever shown by colour alone. Unknown bands show as they came. */
export const bandText = (t: Strings, band: string) => (t as Record<string, string>)[`band_${band}`] ?? band;
