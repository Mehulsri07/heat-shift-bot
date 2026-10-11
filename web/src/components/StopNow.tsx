import { useEffect } from 'react';
import type { StopWindow } from '../api';
import { fill, type Strings } from '../copy';

interface Props {
  t: Strings;
  stop: StopWindow;
}

/** Three short beeps. Silent when the browser blocks sound before the first tap; the banner still shows. */
function playAlert() {
  try {
    const audio = new AudioContext();
    for (const at of [0, 0.35, 0.7]) {
      const beep = audio.createOscillator();
      const volume = audio.createGain();
      beep.frequency.value = 880;
      volume.gain.value = 0.3;
      beep.connect(volume).connect(audio.destination);
      beep.start(audio.currentTime + at);
      beep.stop(audio.currentTime + at + 0.2);
    }
    setTimeout(() => audio.close(), 1500);
  } catch {
    // no sound on this device
  }
}

/**
 * Shown on today's plan while the current hour is inside the API's stop-work window.
 * ponytail: only while the app is open; an alarm with the app closed needs local notifications.
 */
export function StopNow({ t, stop }: Props) {
  useEffect(playAlert, []);
  return (
    <section className="stopnow" role="alert">
      <h2 className="stopnow-title">{t.stop_now_title}</h2>
      <p className="stopnow-until">{fill(t.stop_now_until, { end: stop.end })}</p>
    </section>
  );
}
