import type { CSSProperties } from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { MotionProps } from "./types";

// One composition is shared by the live Player and the server renderer.
// All motion is frame-driven; no timers, random values, network fonts or CSS transitions.
export function MotionScene({ insert: i, imageUrls }: MotionProps) {
  const frame = useCurrentFrame();
  const { width, height, durationInFrames, fps } = useVideoConfig();
  const progress = frame / Math.max(1, durationInFrames - 1);
  const enter = interpolate(
    frame,
    [0, Math.max(1, Math.min(fps * 0.65, durationInFrames * 0.25))],
    [0, 1],
    { extrapolateRight: "clamp" },
  );
  const ease = 1 - Math.pow(1 - enter, 3);
  const base = Math.min(width / 1280, height / 720);
  const pad = 64 * base;
  const line: CSSProperties = {
    width: 72 * base * ease,
    height: 4 * base,
    background: i.accent,
    marginBottom: 26 * base,
  };
  const eyebrow: CSSProperties = {
    color: i.accent,
    fontSize: 18 * base,
    letterSpacing: 3 * base,
    fontWeight: 700,
    marginBottom: 22 * base,
  };
  const title: CSSProperties = {
    fontSize: 58 * base,
    lineHeight: 1.15,
    fontWeight: 750,
    margin: 0,
    overflowWrap: "anywhere",
  };
  const source: CSSProperties = {
    color: "#c7cfda",
    fontSize: 18 * base,
    overflowWrap: "anywhere",
  };
  const showImage = (index: number, style: CSSProperties = {}) => {
    const url = imageUrls[index];
    const imageStyle: CSSProperties = {
      width: "100%",
      height: "100%",
      objectFit: "cover",
      transform: `translateX(${i.pan * progress}%) scale(${1 + (i.zoom - 1) * progress}) rotate(${i.rotation * progress}deg)`,
      filter: `brightness(${i.brightness}) saturate(${i.saturation}) blur(${i.blur * base}px)`,
      ...style,
    };
    return url ? (
      <Img
        src={url.startsWith("static:") ? staticFile(url.slice(7)) : url}
        style={imageStyle}
      />
    ) : (
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          background: "#233142",
          color: "#aebfd2",
          fontSize: 28 * base,
        }}
      >
        Wybierz zdjęcie {index + 1}
      </AbsoluteFill>
    );
  };
  return (
    <AbsoluteFill
      style={{
        background: i.background,
        color: "#f3f5f8",
        fontFamily: "Arial, sans-serif",
        overflow: "hidden",
      }}
    >
      {i.template === "photo" && (
        <>
          <AbsoluteFill style={{ overflow: "hidden" }}>
            {showImage(0)}
          </AbsoluteFill>
          <AbsoluteFill
            style={{
              background: "linear-gradient(transparent 30%, rgba(0,0,0,.82))",
            }}
          />
          <div
            style={{
              position: "absolute",
              bottom: pad,
              left: pad,
              right: pad,
              opacity: ease,
              transform: `translateY(${(1 - ease) * 24 * base}px)`,
            }}
          >
            <div style={line} />
            <h1 style={title}>{i.title}</h1>
            <p style={{ fontSize: 26 * base, marginBottom: 0 }}>{i.subtitle}</p>
            {i.source && <p style={source}>{i.source}</p>}
          </div>
        </>
      )}
      {i.template === "compare" && (
        <>
          {[0, 1].map((n) => (
            <div
              key={n}
              style={{
                position: "absolute",
                top: 0,
                bottom: 0,
                left: `${n * 50}%`,
                width: "50%",
                overflow: "hidden",
              }}
            >
              {showImage(n)}
              <div
                style={{
                  position: "absolute",
                  inset: 0,
                  background: "linear-gradient(transparent 45%,rgba(0,0,0,.8))",
                }}
              />
              <div
                style={{
                  position: "absolute",
                  bottom: pad,
                  left: pad * 0.65,
                  right: pad * 0.65,
                  opacity: ease,
                }}
              >
                <span
                  style={{
                    ...eyebrow,
                    color: "white",
                    background: i.background,
                    padding: 12 * base,
                    display: "inline-block",
                  }}
                >
                  {i.labels[n]}
                </span>
              </div>
            </div>
          ))}
          <div
            style={{
              position: "absolute",
              top: 0,
              bottom: 0,
              left: "50%",
              width: 4 * base,
              background: i.accent,
              transform: "translateX(-50%)",
            }}
          />
          <div
            style={{
              position: "absolute",
              top: pad * 0.6,
              left: pad,
              right: pad,
              textShadow: "0 2px 16px black",
              opacity: ease,
            }}
          >
            <h1 style={{ ...title, fontSize: 40 * base }}>{i.title}</h1>
            <p style={{ ...source, color: "white" }}>{i.subtitle}</p>
          </div>
          {i.source && (
            <div
              style={{
                ...source,
                position: "absolute",
                bottom: 16 * base,
                left: pad,
              }}
            >
              {i.source}
            </div>
          )}
        </>
      )}
      {i.template === "chart" && (
        <div
          style={{
            position: "absolute",
            inset: pad,
            display: "flex",
            flexDirection: "column",
          }}
        >
          <div style={line} />
          <h1 style={{ ...title, fontSize: 42 * base }}>{i.title}</h1>
          <p style={{ ...source, marginTop: 12 * base }}>{i.subtitle}</p>
          <div
            style={{
              display: "flex",
              flex: 1,
              gap: 20 * base,
              alignItems: "stretch",
              marginTop: 30 * base,
              marginBottom: 20 * base,
              minHeight: 0,
            }}
          >
            {i.data.map((d, n) => {
              const amount = Math.max(
                0,
                Math.min(1, (ease - n * 0.045) / 0.68),
              );
              const maximum = Math.max(1, ...i.data.map((d) => d.value));
              return (
                <div
                  key={n}
                  style={{
                    flex: 1,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    minWidth: 0,
                  }}
                >
                  <div
                    style={{
                      flex: 1,
                      width: "100%",
                      display: "flex",
                      flexDirection: "column",
                      justifyContent: "flex-end",
                      alignItems: "center",
                      minHeight: 0,
                    }}
                  >
                    <div
                      style={{
                        fontSize: 22 * base,
                        fontWeight: 700,
                        marginBottom: 10 * base,
                        whiteSpace: "nowrap",
                      }}
                    >
                      {new Intl.NumberFormat("pl-PL", {
                        maximumFractionDigits: 1,
                        notation: d.value >= 1e6 ? "compact" : "standard",
                      }).format(d.value * amount)}
                      {i.unit && ` ${i.unit}`}
                    </div>
                    <div
                      style={{
                        width: "80%",
                        height: `${Math.max(0.5, (d.value / maximum) * 70 * amount)}%`,
                        background: i.accent,
                        borderRadius: `${6 * base}px ${6 * base}px 0 0`,
                        opacity: 0.7 + (n / Math.max(1, i.data.length)) * 0.3,
                      }}
                    />
                  </div>
                  <div
                    style={{
                      width: "100%",
                      height: 2 * base,
                      background: "#455164",
                    }}
                  />
                  <div
                    style={{
                      fontSize: 18 * base,
                      marginTop: 14 * base,
                      textAlign: "center",
                      overflowWrap: "anywhere",
                    }}
                  >
                    {d.label}
                  </div>
                </div>
              );
            })}
          </div>
          {i.source && <div style={source}>{i.source}</div>}
        </div>
      )}
      {i.template === "quote" && (
        <div
          style={{
            position: "absolute",
            inset: pad,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            opacity: ease,
            transform: `translateY(${(1 - ease) * 25 * base}px)`,
          }}
        >
          <div style={{ ...eyebrow, marginBottom: 16 * base }}>{i.title}</div>
          <div
            style={{ fontSize: 100 * base, color: i.accent, height: 85 * base }}
          >
            “
          </div>
          <div
            style={{
              fontSize: (i.text.length > 160 ? 36 : 46) * base,
              lineHeight: 1.4,
              fontWeight: 600,
              overflowWrap: "anywhere",
            }}
          >
            {i.text || "Wpisz cytat w panelu obok."}
          </div>
          <div style={{ ...line, marginTop: 30 * base }} />
          <div style={{ fontSize: 24 * base }}>{i.subtitle}</div>
          <p style={source}>{i.source}</p>
        </div>
      )}
      {i.template === "chapter" && (
        <>
          <div
            style={{
              position: "absolute",
              width: height * 0.8,
              height: height * 0.8,
              right: -height * 0.25,
              top: height * 0.1,
              border: `${2 * base}px solid ${i.accent}`,
              borderRadius: "50%",
              opacity: 0.16,
              transform: `scale(${0.9 + 0.15 * progress})`,
            }}
          />
          <div
            style={{
              position: "absolute",
              inset: pad,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              opacity: ease,
              transform: `translateX(${(1 - ease) * -32 * base}px)`,
            }}
          >
            <div style={eyebrow}>{i.text || "KOLEJNY ROZDZIAŁ"}</div>
            <div style={line} />
            <h1 style={{ ...title, fontSize: 72 * base, maxWidth: "88%" }}>
              {i.title}
            </h1>
            <p
              style={{
                fontSize: 28 * base,
                lineHeight: 1.4,
                color: "#c7cfda",
                maxWidth: "85%",
              }}
            >
              {i.subtitle}
            </p>
            {i.source && <p style={source}>{i.source}</p>}
          </div>
        </>
      )}
    </AbsoluteFill>
  );
}
