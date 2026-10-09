import { errorText, type Strings } from '../copy';

interface Props {
  t: Strings;
  code: string;
  onRetry: () => void;
}

/** The plan could not be shown. The sentence comes from the copy file for the API's error code. */
export function Failed({ t, code, onRetry }: Props) {
  return (
    <div className="failed" role="alert">
      <p className="failed-title">{errorText(t, code)}</p>
      <button type="button" className="button" onClick={onRetry}>
        {t.retry}
      </button>
    </div>
  );
}
