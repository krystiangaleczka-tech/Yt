import { useEffect, useState } from "react";
import type { ImgHTMLAttributes } from "react";

// Match layout_cutout's alpha.getbbox() instead of positioning an entire PNG canvas.
export default function PaperCutoutPreview({ src, style, ...props }: ImgHTMLAttributes<HTMLImageElement>) {
  const [cropped, setCropped] = useState("");
  useEffect(() => {
    let active = true;
    let url = "";
    setCropped("");
    const image = new Image();
    image.onload = () => {
      if (!active) return;
      const canvas = document.createElement("canvas");
      canvas.width = image.naturalWidth; canvas.height = image.naturalHeight;
      const context = canvas.getContext("2d", { willReadFrequently: true });
      if (!context) return;
      context.drawImage(image, 0, 0);
      try {
        const data = context.getImageData(0, 0, canvas.width, canvas.height).data;
        let left = canvas.width, top = canvas.height, right = -1, bottom = -1;
        for (let y = 0; y < canvas.height; y++) for (let x = 0; x < canvas.width; x++) {
          if (data[(y * canvas.width + x) * 4 + 3] > 0) {
            left = Math.min(left, x); top = Math.min(top, y);
            right = Math.max(right, x); bottom = Math.max(bottom, y);
          }
        }
        if (right < left) return;
        const cutout = document.createElement("canvas");
        cutout.width = right - left + 1; cutout.height = bottom - top + 1;
        cutout.getContext("2d")?.drawImage(image, left, top, cutout.width, cutout.height, 0, 0, cutout.width, cutout.height);
        cutout.toBlob(blob => {
          if (!active || !blob) return;
          url = URL.createObjectURL(blob); setCropped(url);
        });
      } catch { /* Failed decoding must not present a false full-canvas placement. */ }
    };
    if (src) image.src = src;
    return () => { active = false; if (url) URL.revokeObjectURL(url); };
  }, [src]);
  return <img {...props} src={cropped || undefined} style={{ ...style, visibility: cropped ? "visible" : "hidden" }} />;
}
