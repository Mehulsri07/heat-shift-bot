import type { StopWindow } from '../api';

/** True when an hour falls inside the stop-work window. Compares the API's HH:MM strings. */
export const isStopped = (hour: string, stop: StopWindow | null) =>
  stop !== null && hour >= stop.start && hour < stop.end;

/** The hour as two digits for the axis, e.g. "07". */
export const hourLabel = (hour: string) => hour.slice(0, 2);
