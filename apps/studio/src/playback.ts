import type { Clip, Project } from "./types";

export type PlaybackMedia = Pick<
  HTMLMediaElement,
  | "currentTime"
  | "playbackRate"
  | "paused"
  | "ended"
  | "seeking"
  | "readyState"
  | "play"
  | "pause"
>;

type State = {
  key: string;
  playing: boolean;
  pending: boolean;
  failed: boolean;
  target: number | null;
  generation: number;
};
const states = new WeakMap<PlaybackMedia, State>();

/** Seek on transport/clip changes, never to chase individual video frames. */
export function syncMedia(
  media: PlaybackMedia,
  seconds: number,
  playing: boolean,
  speed: number,
  key: string,
  onError: (error: unknown) => void,
) {
  let state = states.get(media);
  const changed = !state || state.key !== key;
  if (!state || changed) {
    state = {
      key,
      playing: false,
      pending: false,
      failed: false,
      target: null,
      generation: 0,
    };
    states.set(media, state);
  }
  const starting = playing && !state.playing;
  const rateChanged = media.playbackRate !== speed;
  if (rateChanged) media.playbackRate = speed;
  const sameTarget =
    state.target !== null && Math.abs(state.target - seconds) < 0.025;
  if (
    (changed || starting || rateChanged || (!playing && !sameTarget)) &&
    Math.abs(media.currentTime - seconds) > 0.025 &&
    !(media.seeking && sameTarget)
  ) {
    media.currentTime = seconds;
  }
  state.target = seconds;
  if (!playing) {
    pauseMedia(media);
    return;
  }
  state.playing = true;
  if (
    !media.paused ||
    state.pending ||
    state.failed ||
    (media.ended && !starting)
  )
    return;
  const attempt = state;
  const generation = ++attempt.generation;
  attempt.pending = true;
  void media.play().then(
    () => {
      // A play promise may finish after Pause, removal or a source replacement.
      const latest = states.get(media);
      if (!latest?.playing) media.pause();
      if (latest === attempt && generation === attempt.generation)
        attempt.pending = false;
    },
    (error: unknown) => {
      if (
        states.get(media) !== attempt ||
        generation !== attempt.generation ||
        !attempt.playing
      )
        return;
      attempt.pending = false;
      attempt.failed = true;
      onError(error);
    },
  );
}

export function pauseMedia(media: PlaybackMedia) {
  const state = states.get(media);
  const pending = state?.pending;
  if (state) {
    if (state.playing || state.pending) state.generation++;
    state.playing = false;
    state.pending = false;
    state.failed = false;
  }
  if (!media.paused || pending) media.pause();
}

export function primaryAudioClip(
  project: Project,
  frame: number,
): Clip | undefined {
  const solo = project.sequence.tracks.some((track) => track.solo);
  const tracks = project.sequence.tracks.filter(
    (track) => track.kind === "audio" && !track.muted && (!solo || track.solo),
  );
  return project.sequence.clips
    .filter(
      (clip) =>
        clip.asset_id &&
        tracks.some((track) => track.id === clip.track_id) &&
        frame >= clip.start &&
        frame < clip.start + clip.duration,
    )
    .sort((a, b) => {
      const priority = (clip: Clip) =>
        tracks.find((track) => track.id === clip.track_id)?.role === "narration"
          ? 0
          : 1;
      return (
        priority(a) - priority(b) ||
        a.start - b.start ||
        a.id.localeCompare(b.id)
      );
    })[0];
}

/** A stalled/starting audio clock holds the picture without repeatedly seeking sound. */
export function audioFrame(
  clip: Clip,
  media: PlaybackMedia | undefined,
  rate: number,
  previous: number,
) {
  if (!media) return previous;
  if (media.ended) return clip.start + clip.duration;
  if (media.paused || media.seeking || media.readyState < 2) return previous;
  const frame =
    clip.start +
    Math.floor((media.currentTime * rate - clip.source_in) / clip.speed);
  return Math.max(
    previous,
    Math.min(clip.start + clip.duration, Math.max(clip.start, frame)),
  );
}
