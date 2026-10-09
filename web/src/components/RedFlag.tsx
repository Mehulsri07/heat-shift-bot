import type { Strings } from '../copy';

interface Props {
  t: Strings;
  text: string;
}

/** The fixed heat-stroke warning. Shown word for word, with its line breaks, and never restyled to hide it. */
export function RedFlag({ t, text }: Props) {
  return (
    <section className="redflag" role="note" aria-labelledby="redflag-title">
      <h2 id="redflag-title" className="redflag-title">
        {t.red_flag_heading}
      </h2>
      <p className="redflag-text">{text}</p>
    </section>
  );
}
