import { useState } from "react";
import { Music2, Search } from "lucide-react";
import { Button } from "./components";
import { castImage } from "./animationTypes";
import type { CastBank, StageScene } from "./animationTypes";

export default function StageAssets({
  scene,
  bank,
  channelId,
  update,
}: {
  scene: StageScene;
  bank: CastBank;
  channelId: string;
  update: (changes: Partial<StageScene>) => void;
}) {
  const [query, setQuery] = useState("");
  const matches = (name: string) =>
    name.toLocaleLowerCase("pl").includes(query.toLocaleLowerCase("pl"));
  return (
    <aside className="shot-assets">
      <div className="shot-panel-heading">
        <strong>Assety</strong>
        <span className="small muted">Bank kanału</span>
      </div>
      <label className="scene-search">
        <Search size={14} />
        <input
          aria-label="Szukaj w banku assetów"
          value={query}
          placeholder="Szukaj assetu…"
          onChange={(e) => setQuery(e.target.value)}
        />
      </label>
      <h2>Lokacje i tła</h2>
      <div className="shot-asset-list">
        {bank.locations
          .filter((location) => !location.archived && matches(location.name))
          .flatMap((location) =>
            location.states.map((state) => (
              <button
                className="shot-asset"
                key={state.id}
                onClick={() =>
                  update({
                    location_id: location.id,
                    location_state_id: state.id,
                  })
                }
              >
                {state.image && (
                  <img alt="" src={castImage(channelId, state.image.file)} />
                )}
                <span className="small">
                  {location.name} · {state.name}
                </span>
              </button>
            )),
          )}
      </div>
      <h2>Postacie</h2>
      <div className="shot-asset-list">
        {bank.characters
          .filter((character) => !character.archived && matches(character.name))
          .map((character) => {
            const pose =
              character.poses.find(
                (item) => item.id === character.default_pose_id,
              ) || character.poses[0];
            return (
              <button
                className="shot-asset"
                key={character.id}
                disabled={!pose || scene.characters.length >= 8}
                onClick={() =>
                  update({
                    characters: [
                      ...scene.characters,
                      {
                        character_id: character.id,
                        pose_id: pose.id,
                        x: 0.5,
                        y: 0.9,
                        scale: 0.6,
                        flip: false,
                        motion: "idle",
                      },
                    ],
                  })
                }
              >
                {pose && (
                  <img alt="" src={castImage(channelId, pose.image.file)} />
                )}
                <span className="small">+ {character.name}</span>
              </button>
            );
          })}
      </div>
      <h2>Rekwizyty i nakładki</h2>
      <div className="shot-asset-list">
        {(bank.items || [])
          .filter(
            (item) =>
              !item.archived &&
              item.category !== "costume" &&
              matches(item.name),
          )
          .flatMap((item) =>
            item.variants.map((variant) => (
              <button
                className="shot-asset"
                key={variant.id}
                disabled={(scene.props?.length || 0) >= 20}
                onClick={() =>
                  update({
                    props: [
                      ...(scene.props || []),
                      {
                        item_id: item.id,
                        variant_id: variant.id,
                        x: 0.5,
                        y: 0.6,
                        scale: 0.3,
                        rotation: 0,
                        layer: "front",
                        motion: "appear",
                        at: 0,
                      },
                    ],
                  })
                }
              >
                <img alt="" src={castImage(channelId, variant.image.file)} />
                <span className="small">
                  + {item.name} · {variant.name}
                </span>
              </button>
            )),
          )}
      </div>
      <h2>Dźwięki</h2>
      {(bank.sounds || [])
        .filter(
          (sound) =>
            !sound.archived && sound.kind !== "music" && matches(sound.name),
        )
        .map((sound) => (
          <Button
            key={sound.id}
            icon={Music2}
            disabled={(scene.audio?.length || 0) >= 20}
            onClick={() =>
              update({
                audio: [
                  ...(scene.audio || []),
                  {
                    sound_id: sound.id,
                    at: 0,
                    volume: sound.kind === "ambience" ? 0.1 : 1,
                  },
                ],
              })
            }
          >
            {sound.name}
          </Button>
        ))}
      {!bank.locations.length && !bank.characters.length && (
        <p className="muted small">Dodaj lokacje i postacie w banku kanału.</p>
      )}
    </aside>
  );
}
