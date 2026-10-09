import { Capacitor } from '@capacitor/core';
import { Directory, Filesystem } from '@capacitor/filesystem';
import { Share } from '@capacitor/share';

export const isNativeApp = Capacitor.isNativePlatform();

const FILE_NAME = 'crew-voice-note.mp3';

/**
 * Share the crew voice note. In the Android app the MP3 itself goes to the share sheet,
 * so WhatsApp receives an audio file; in a browser only its link can be shared.
 * Returns false when sharing is not available, so the caller can fall back to a plain link.
 */
export async function shareVoiceNote(url: string, title: string): Promise<boolean> {
  try {
    if (isNativeApp) {
      // ponytail: downloadFile is deprecated since Filesystem 7.1 but still ships;
      // move to @capacitor/file-transfer if a later version removes it.
      await Filesystem.downloadFile({ url, path: FILE_NAME, directory: Directory.Cache });
      const { uri } = await Filesystem.getUri({ path: FILE_NAME, directory: Directory.Cache });
      await Share.share({ title, files: [uri] });
      return true;
    }
    if (navigator.share) {
      await navigator.share({ title, url });
      return true;
    }
  } catch (err) {
    // Closing the share sheet without picking an app is not a failure.
    if (err instanceof Error && (err.name === 'AbortError' || /cancel/i.test(err.message))) return true;
  }
  return false;
}
