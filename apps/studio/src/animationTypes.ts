export type ProductionMode = "documentary" | "animation_2d" | "broll";
export const modeLabels: Record<ProductionMode, string> = {
  documentary: "Dokument",
  animation_2d: "Animacja 2D",
  broll: "B-roll",
};
export type CastImage = {
  file: string;
  width: number;
  height: number;
  alpha: boolean;
};
export type Pose = {
  id: string;
  name: string;
  view: "front" | "three_quarter" | "side" | "back";
  image: CastImage;
  tags: string[];
};
export const viewLabels: Record<Pose["view"], string> = {
  front: "Przód",
  three_quarter: "3/4",
  side: "Profil",
  back: "Tył",
};
export type Character = {
  id: string;
  revision: number;
  channel_id: string;
  name: string;
  role: string;
  description: string;
  personality: string;
  goal: string;
  signature: string;
  color: string;
  voice: { provider: "" | "elevenlabs" | "local"; voice_id: string; notes: string };
  poses: Pose[];
  default_pose_id: string;
  archived: boolean;
  updated_at: string;
};
export type LocationState = {
  id: string;
  name: string;
  description: string;
  time_of_day: "" | "day" | "dusk" | "night";
  image: CastImage | null;
  foreground?: CastImage | null;
};
export type Location = {
  id: string;
  revision: number;
  channel_id: string;
  name: string;
  description: string;
  states: LocationState[];
  archived: boolean;
  updated_at: string;
};
export type CastBank = { characters: Character[]; locations: Location[] };
export type StageCharacter = {
  character_id: string;
  pose_id: string;
  x: number;
  y: number;
  scale: number;
  flip: boolean;
  motion?: ActorMotion;
};
export type ActorMotion =
  | "idle"
  | "still"
  | "enter_left"
  | "enter_right"
  | "exit_left"
  | "exit_right";
export const actorMotionLabels: Record<ActorMotion, string> = {
  idle: "Oddycha",
  still: "Bez ruchu",
  enter_left: "Wchodzi z lewej",
  enter_right: "Wchodzi z prawej",
  exit_left: "Wychodzi w lewo",
  exit_right: "Wychodzi w prawo",
};
export type CameraMove =
  | "static"
  | "push_in"
  | "pull_out"
  | "pan_left"
  | "pan_right"
  | "shake";
export const cameraLabels: Record<CameraMove, string> = {
  static: "Statyczna",
  push_in: "Najazd",
  pull_out: "Odjazd",
  pan_left: "Panorama w lewo",
  pan_right: "Panorama w prawo",
  shake: "Drgania",
};
export type DialogueLine = {
  id?: string;
  speaker: string;
  text: string;
  direction: string;
};
export type SceneStatus = "draft" | "review" | "approved" | "rework";
export type StageScene = {
  id: string;
  number: number;
  beat_id: string;
  title: string;
  story_time: string;
  location_id: string;
  location_state_id: string;
  characters: StageCharacter[];
  action: string;
  camera: string;
  dialogue: DialogueLine[];
  sound: { ambience: string; music: string; sfx: string[] };
  motion?: { camera: CameraMove; strength: number };
  seconds: number;
  status: SceneStatus;
  reviews: {
    status: "approved" | "rework";
    note: string;
    tags: string[];
    at: string;
  }[];
};
export const statusLabels: Record<SceneStatus, string> = {
  draft: "Szkic",
  review: "Do oceny",
  approved: "Zatwierdzona",
  rework: "Do poprawki",
};
export const reviewTags = [
  "Kadr",
  "Postać/poza",
  "Tło",
  "Dialog",
  "Dźwięk",
  "Tempo",
] as const;
export const castImage = (channelId: string, file: string) =>
  `/api/channels/${channelId}/cast-media/${file}`;
