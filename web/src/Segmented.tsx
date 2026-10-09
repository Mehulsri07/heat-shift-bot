interface Option<T extends string> {
  value: T;
  label: string;
}

interface Props<T extends string> {
  name: string;
  legend: string;
  /** Hide the legend visually; it is still read out. */
  quiet?: boolean;
  /** `tabs` and `compact` are the two forms used inside the blue header. */
  variant?: 'tabs' | 'compact';
  value: T | null;
  options: Option<T>[];
  onChange: (value: T) => void;
}

/** A two-or-three way choice drawn as joined blocks. Real radio inputs underneath. */
export function Segmented<T extends string>({ name, legend, quiet, variant, value, options, onChange }: Props<T>) {
  return (
    <fieldset className={variant ? `segmented segmented-${variant}` : 'segmented'}>
      <legend className={quiet ? 'visually-hidden' : 'field-label'}>{legend}</legend>
      <div className="segmented-row">
        {options.map((option) => (
          <label key={option.value} className="segment">
            <input
              type="radio"
              name={name}
              value={option.value}
              checked={value === option.value}
              onChange={() => onChange(option.value)}
              required
            />
            <span>{option.label}</span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}
