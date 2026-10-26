import { Composition, registerRoot } from "remotion";
import { MotionScene } from "./MotionScene";
import { makeInsert } from "./types";

registerRoot(() => (
  <Composition
    id="DocosInsert"
    component={MotionScene}
    width={1280}
    height={720}
    fps={30}
    durationInFrames={180}
    defaultProps={{
      insert: makeInsert("insert_0000000000000000", "chapter"),
      imageUrls: [] as string[],
    }}
    calculateMetadata={({ props }) => ({
      durationInFrames: props.insert.duration,
    })}
  />
));
