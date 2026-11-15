/**
 * Teatr papierowy na żywo: ujęcia rysowane kodem zamiast klipów mp4.
 *
 * Python (output/<film>/na_zywo.py, uruchamiany przez studio_api/teatr.py) liczy ruch ujęcia: dla każdej klatki
 * listę wycinków w pikselach ekranu (miejsce, skala, obrót, rozmycie, cień, barwa) plus światło. Tutaj karta graficzna
 * (WebGL2) rysuje z tego klatkę 1280 × 720 tymi samymi wzorami co papier.Stage (cienie, głębia ostrości, światło,
 * winieta, ziarno) — kilka ms zamiast ok. 450 ms w Pythonie. Po zapisaniu kodu ujęcia serwer liczy ruch od nowa,
 * a podgląd sam się odświeża. Klipy mp4 zostają na osi jako zapas i do renderu końcowego.
 */
import type { Project } from "./types";

type Wycinek = { plik: string; w: number; h: number; tw: number; th: number; nazwa: string };
type Linia = { p: number[]; w: number; c: number[]; a: number; i: number };
type Klatka = {
  t: number;
  gr: [number, number, number];
  dim: number;
  spot: [number, number, number, number] | null;
  ns: number;
  napis: string | null;
  e: number[][];
  l: Linia[];
};
type Dane = { numer: number; klucz: string; odn: string; kod: number; T: number; fps: number; w: number; h: number; wycinki: Wycinek[]; klatki: Klatka[] };
export type StanTeatru = {
  dostepny: boolean;
  kod?: number;
  stan?: string;
  blad?: string;
  gotowe?: number;
  ujec?: number;
  moduly?: string[];
  czas?: number;
};

const W = 1280,
  H = 720;
const SHADOW = [0.16, 0.09, 0.05],
  HAZE = [0.93, 0.83, 0.66];
const BUDZET = 420e6; // bajty tekstur na karcie (z mipmapami) — reszta wycinków wraca z pamięci podręcznej przeglądarki

const VS_SPRITE = `#version 300 es
in vec2 c;
uniform vec2 S, K, R, A, size, off, scr;
uniform float pad;
out vec2 uv;
void main() {
  vec2 e = (c * 2.0 - 1.0) * pad / max(abs(K), vec2(1e-4));
  vec2 local = c * size - A * size + e;
  vec2 d = local * K;
  vec2 p = S + vec2(R.x * d.x - R.y * d.y, R.y * d.x + R.x * d.y) + off;
  uv = (local + A * size) / size;
  gl_Position = vec4(p.x / scr.x * 2.0 - 1.0, 1.0 - p.y / scr.y * 2.0, 0.0, 1.0);
}`;
const FS_SPRITE = `#version 300 es
precision highp float;
in vec2 uv;
uniform sampler2D tex;
uniform vec2 pxUV;
uniform float tpp, radius, alpha, haze, mode, cien, sila;
uniform vec3 tint, shadowCol, hazeCol;
out vec4 o;
vec4 tap(vec2 q, float lod) {
  if (q.x < 0.0 || q.y < 0.0 || q.x > 1.0 || q.y > 1.0) return vec4(0.0);
  return textureLod(tex, q, lod);
}
vec4 probka(float r) {
  if (r < 0.35) return tap(uv, log2(max(tpp, 1.0)) - 0.25);
  float lod = log2(max(1.0, max(tpp, tpp * r * 0.55)));
  vec4 s = tap(uv, lod) * 0.16;
  for (int i = 0; i < 4; i++) {
    float a = float(i) * 1.5708 + 0.785;
    s += tap(uv + vec2(cos(a), sin(a)) * pxUV * r * 0.6, lod) * 0.12;
  }
  for (int i = 0; i < 8; i++) {
    float a = float(i) * 0.7854;
    s += tap(uv + vec2(cos(a), sin(a)) * pxUV * r * 1.3, lod) * 0.045;
  }
  return s;
}
void main() {
  vec4 t = probka(radius);
  if (cien > 0.5) { float a = t.a * sila; o = vec4(shadowCol * a, a); return; }
  vec3 rgb = t.rgb * tint;
  float a = t.a;
  rgb += (hazeCol * a - rgb) * haze;
  rgb *= alpha; a *= alpha;
  if (mode < 0.5) o = vec4(rgb, a);
  else if (mode < 1.5) o = vec4(rgb, 0.0);
  else o = vec4(1.0 - a + rgb, 1.0);
}`;
const VS_LINIA = `#version 300 es
in vec2 p;
in vec4 col;
uniform vec2 scr;
out vec4 c;
void main() { c = col; gl_Position = vec4(p.x / scr.x * 2.0 - 1.0, 1.0 - p.y / scr.y * 2.0, 0.0, 1.0); }`;
const FS_LINIA = `#version 300 es
precision highp float;
in vec4 c;
out vec4 o;
void main() { o = vec4(c.rgb * c.a, c.a); }`;
const VS_PELNY = `#version 300 es
in vec2 c;
void main() { gl_Position = vec4(c * 2.0 - 1.0, 0.0, 1.0); }`;
const FS_POST = `#version 300 es
precision highp float;
uniform sampler2D scena;
uniform vec2 scr;
uniform vec3 grade;
uniform float dim, ziarno;
uniform vec4 spot;
out vec4 o;
float hash(vec2 p) { p = fract(p * vec2(123.34, 456.21)); p += dot(p, p + 45.32); return fract(p.x * p.y); }
void main() {
  vec2 f = gl_FragCoord.xy;
  vec3 c = texture(scena, f / scr).rgb;
  float x = f.x, y = scr.y - f.y;
  if (spot.z > 0.0) {
    float d = sqrt(pow(x - spot.x, 2.0) + pow((y - spot.y) * 1.15, 2.0)) / spot.z;
    c *= 1.0 - spot.w * pow(clamp(d - 0.35, 0.0, 1.0), 1.3);
  }
  float key = 1.05 - 0.13 * (x / scr.x) - 0.10 * (y / scr.y);
  float vig = 1.0 - 0.34 * pow(pow((x - scr.x * 0.5) / (scr.x * 0.5), 2.0) + pow((y - scr.y * 0.5) / (scr.y * 0.5), 2.0), 1.25);
  c *= key * clamp(vig, 0.3, 1.0);
  c *= grade * dim;
  c = clamp(c, 0.0, 1.0);
  c += 0.10 * (c * c * (3.0 - 2.0 * c) - c);
  c += (hash(f + ziarno * 17.13) - 0.5) * 0.038;
  o = vec4(c, 1.0);
}`;

type Program = { p: WebGLProgram; u: Record<string, WebGLUniformLocation> };
type Tekstura = { t: WebGLTexture; bajty: number; uzyte: number };

/** Odcinek ujęcia w projekcie: scene.legacy.teatr = {film, jezyk, odn}. */
export function odnSceny(project: Project, sceneId?: string | null): string | null {
  if (!sceneId) return null;
  const s = project.scenes.find((x) => x.id === sceneId);
  const t = s?.legacy?.teatr as { odn?: string } | undefined;
  return t && typeof t.odn === "string" ? t.odn : null;
}

export function maTeatr(project: Project) {
  return project.scenes.some((s) => !!(s.legacy?.teatr as { odn?: string } | undefined)?.odn);
}

const KLUCZ_TRYBU = "docos-teatr-na-zywo";
/** Przełącznik „na żywo / klip mp4” (domyślnie na żywo), wspólny dla Ujęć i Montażu. */
export function naZywoWlaczone() {
  try {
    return localStorage.getItem(KLUCZ_TRYBU) !== "0";
  } catch {
    return true;
  }
}
export function ustawNaZywo(on: boolean) {
  try {
    localStorage.setItem(KLUCZ_TRYBU, on ? "1" : "0");
  } catch {
    /* tryb prywatny: przełącznik działa do przeładowania */
  }
  for (const t of TEATRY.values()) t.powiadom();
}

function zawin(txt: string, n = 60) {
  const out: string[] = [];
  let line = "";
  for (const w of txt.split(/\s+/)) {
    if (line.length + w.length + 1 > n && line) {
      out.push(line);
      line = w;
    } else line = (line + " " + w).trim();
  }
  out.push(line);
  return out;
}

export class Teatr {
  stan: StanTeatru = { dostepny: false };
  private gl: WebGL2RenderingContext | null = null;
  private glCanvas = document.createElement("canvas");
  private out = document.createElement("canvas");
  private ctx = this.out.getContext("2d")!;
  private P: { spr: Program; lin: Program; post: Program } | null = null;
  private vaoKw: WebGLVertexArrayObject | null = null;
  private vaoLin: WebGLVertexArrayObject | null = null;
  private linBuf: WebGLBuffer | null = null;
  private fbo: WebGLFramebuffer | null = null;
  private fboTex: WebGLTexture | null = null;
  private dane = new Map<string, Dane>();
  private gotowe = new Set<string>(); // odn, którego wszystkie tekstury są na karcie
  private wToku = new Map<string, Promise<void>>();
  private tekstury = new Map<string, Tekstura>();
  private wczytywane = new Map<string, Promise<Tekstura>>();
  private sluchacze = new Set<() => void>();
  private ostatnia = "";
  private tik = 0;
  private dziala = false; // jedna pętla sprawdzania stanu na teatr, choćby słuchaczy było wielu
  private uzywane = new Map<string, number>(); // odn → kiedy ostatnio potrzebne (do przeliczenia po zmianie kodu)
  bladGL = "";

  constructor(private pid: string) {
    this.glCanvas.width = this.out.width = W;
    this.glCanvas.height = this.out.height = H;
  }

  subskrybuj(fn: () => void) {
    this.sluchacze.add(fn);
    if (!this.dziala) {
      this.dziala = true;
      void this.sprawdz();
    }
    return () => {
      this.sluchacze.delete(fn);
    };
  }
  powiadom() {
    for (const fn of this.sluchacze) fn();
  }

  private async sprawdz() {
    try {
      const r = await fetch(`/api/projects/${this.pid}/teatr/stan`, { cache: "no-store" });
      const s: StanTeatru = r.ok ? await r.json() : { dostepny: false, blad: `Błąd ${r.status}` };
      const zmiana = s.kod !== this.stan.kod || s.stan !== this.stan.stan || s.dostepny !== this.stan.dostepny;
      this.stan = s;
      if (zmiana) {
        // nowa wersja kodu: ujęcia oglądane w ostatnich 20 s liczą się od nowa, stary obraz zostaje do czasu nowego
        const teraz = performance.now();
        for (const [odn, kiedy] of this.uzywane) if (teraz - kiedy < 20000) void this.przygotuj(odn);
        this.powiadom();
      }
    } catch {
      this.stan = { dostepny: false, blad: "Studio nie odpowiada" };
    }
    if (this.sluchacze.size) window.setTimeout(() => void this.sprawdz(), 900);
    else this.dziala = false;
  }

  /** Czy klatki ujęcia można już rysować (ruch policzony, wycinki na karcie). */
  gotowy(odn: string) {
    return this.gotowe.has(odn);
  }

  /** Pobiera ruch ujęcia i jego wycinki (jeśli trzeba — nowsza wersja kodu). */
  przygotuj(odn: string): Promise<void> {
    this.uzywane.set(odn, performance.now());
    const ma = this.dane.get(odn);
    if (ma && this.stan.kod !== undefined && ma.kod === this.stan.kod) return Promise.resolve();
    if (ma && this.stan.stan === "błąd") return Promise.resolve();
    const trwa = this.wToku.get(odn);
    if (trwa) return trwa;
    const zadanie = (async () => {
      try {
        const r = await fetch(`/api/projects/${this.pid}/teatr/ujecie/${odn}`, { cache: "no-store" });
        if (!r.ok) throw new Error(await r.text());
        const d: Dane = await r.json();
        if (!this.init()) return;
        await Promise.all(d.wycinki.map((w) => this.tekstura(w.plik)));
        this.dane.set(odn, d);
        this.gotowe.add(odn);
        this.ostatnia = "";
        this.powiadom();
      } catch (e) {
        this.stan = { ...this.stan, blad: String(e instanceof Error ? e.message : e) };
      } finally {
        this.wToku.delete(odn);
      }
    })();
    this.wToku.set(odn, zadanie);
    return zadanie;
  }

  private init() {
    if (this.gl) return true;
    const gl = this.glCanvas.getContext("webgl2", { antialias: false, premultipliedAlpha: true, preserveDrawingBuffer: true });
    if (!gl) {
      this.bladGL = "Ta przeglądarka nie ma WebGL2 — zostają klipy mp4.";
      return false;
    }
    this.gl = gl;
    const program = (vs: string, fs: string): Program => {
      const p = gl.createProgram()!;
      for (const [type, src] of [
        [gl.VERTEX_SHADER, vs],
        [gl.FRAGMENT_SHADER, fs],
      ] as const) {
        const sh = gl.createShader(type)!;
        gl.shaderSource(sh, src);
        gl.compileShader(sh);
        if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(sh) || "shader");
        gl.attachShader(p, sh);
      }
      gl.linkProgram(p);
      if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p) || "program");
      const u: Record<string, WebGLUniformLocation> = {};
      const n = gl.getProgramParameter(p, gl.ACTIVE_UNIFORMS);
      for (let i = 0; i < n; i++) {
        const a = gl.getActiveUniform(p, i)!;
        u[a.name] = gl.getUniformLocation(p, a.name)!;
      }
      return { p, u };
    };
    this.P = { spr: program(VS_SPRITE, FS_SPRITE), lin: program(VS_LINIA, FS_LINIA), post: program(VS_PELNY, FS_POST) };
    const kw = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, kw);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([0, 0, 1, 0, 0, 1, 1, 1]), gl.STATIC_DRAW);
    this.vaoKw = gl.createVertexArray();
    gl.bindVertexArray(this.vaoKw);
    for (const pr of [this.P.spr, this.P.post]) {
      const loc = gl.getAttribLocation(pr.p, "c");
      gl.enableVertexAttribArray(loc);
      gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    }
    this.linBuf = gl.createBuffer();
    this.vaoLin = gl.createVertexArray();
    gl.bindVertexArray(this.vaoLin);
    gl.bindBuffer(gl.ARRAY_BUFFER, this.linBuf);
    const lp = gl.getAttribLocation(this.P.lin.p, "p"),
      lc = gl.getAttribLocation(this.P.lin.p, "col");
    gl.enableVertexAttribArray(lp);
    gl.vertexAttribPointer(lp, 2, gl.FLOAT, false, 24, 0);
    gl.enableVertexAttribArray(lc);
    gl.vertexAttribPointer(lc, 4, gl.FLOAT, false, 24, 8);
    this.fboTex = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, this.fboTex);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA8, W, H, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
    this.fbo = gl.createFramebuffer();
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.fbo);
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, this.fboTex, 0);
    gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false);
    gl.pixelStorei(gl.UNPACK_COLORSPACE_CONVERSION_WEBGL, gl.NONE);
    return true;
  }

  private tekstura(plik: string): Promise<Tekstura> {
    const ma = this.tekstury.get(plik);
    if (ma) return Promise.resolve(ma);
    const trwa = this.wczytywane.get(plik);
    if (trwa) return trwa;
    const zadanie = (async () => {
      const blob = await (await fetch(`/api/projects/${this.pid}/teatr/wycinki/${plik}`)).blob();
      const bmp = await createImageBitmap(blob, { premultiplyAlpha: "none", colorSpaceConversion: "none" });
      const gl = this.gl!;
      const t = gl.createTexture()!;
      gl.bindTexture(gl.TEXTURE_2D, t);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA8, gl.RGBA, gl.UNSIGNED_BYTE, bmp); // alfa już wymnożona w pliku
      gl.generateMipmap(gl.TEXTURE_2D);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      const tex = { t, bajty: bmp.width * bmp.height * 4 * 1.34, uzyte: ++this.tik };
      bmp.close();
      this.tekstury.set(plik, tex);
      this.wczytywane.delete(plik);
      this.sprzataj();
      return tex;
    })();
    this.wczytywane.set(plik, zadanie);
    return zadanie;
  }

  /** Zwalnia najdawniej używane wycinki, kiedy na karcie jest ich za dużo; ujęcia bez nich wczytają je znowu. */
  private sprzataj() {
    let suma = 0;
    for (const t of this.tekstury.values()) suma += t.bajty;
    if (suma <= BUDZET) return;
    const kolejka = [...this.tekstury.entries()].sort((a, b) => a[1].uzyte - b[1].uzyte);
    for (const [plik, t] of kolejka) {
      if (suma <= BUDZET * 0.8 || this.tik - t.uzyte < 4) break;
      this.gl!.deleteTexture(t.t);
      this.tekstury.delete(plik);
      suma -= t.bajty;
      for (const [odn, d] of this.dane) if (d.wycinki.some((w) => w.plik === plik)) this.gotowe.delete(odn);
    }
  }

  /** Klatka ujęcia w chwili `sekundy` od jego początku (ostatnia klatka stoi do końca ujęcia), z napisem — albo null. */
  klatka(odn: string, sekundy: number): HTMLCanvasElement | null {
    this.uzywane.set(odn, performance.now());
    const d = this.dane.get(odn);
    if (!d || !this.gotowe.has(odn)) {
      void this.przygotuj(odn);
      return null;
    }
    if (this.stan.kod !== undefined && d.kod !== this.stan.kod) void this.przygotuj(odn); // stary obraz, aż przyjdzie nowy
    const n = Math.max(0, Math.min(d.klatki.length - 1, Math.floor(sekundy * d.fps + 1e-6)));
    const klucz = `${odn}:${d.kod}:${n}`;
    if (klucz === this.ostatnia) return this.out;
    const tex = d.wycinki.map((w) => this.tekstury.get(w.plik));
    if (tex.some((t) => !t)) {
      this.gotowe.delete(odn);
      void this.przygotuj(odn);
      return null;
    }
    const tik = ++this.tik;
    for (const t of tex) t!.uzyte = tik;
    this.rysuj(d, d.klatki[n], tex as Tekstura[]);
    this.ctx.clearRect(0, 0, W, H);
    this.ctx.drawImage(this.glCanvas, 0, 0);
    if (d.klatki[n].napis) this.napis(d.klatki[n].napis!);
    this.ostatnia = klucz;
    return this.out;
  }

  /** Napis jak render.subtitle: pasek papieru u dołu kadru. */
  private napis(txt: string) {
    const c = this.ctx,
      lines = zawin(txt),
      lh = 36;
    c.font = "600 28px Baskerville, 'Baskerville Old Face', Georgia, serif";
    const wd = Math.max(...lines.map((l) => c.measureText(l).width)) + 40;
    const y1 = H - 20,
      y0 = y1 - lh * lines.length - 14;
    const rect = (x: number, y: number, w: number, h: number) => {
      c.beginPath();
      c.roundRect(x, y, w, h, 4);
      c.fill();
    };
    c.fillStyle = "rgba(20,12,8,0.35)";
    rect(W / 2 - wd / 2 + 3, y0 + 4, wd, y1 - y0);
    c.fillStyle = "rgba(238,224,192,0.93)";
    rect(W / 2 - wd / 2, y0, wd, y1 - y0);
    c.fillStyle = "rgb(44,28,22)";
    c.textAlign = "center";
    c.textBaseline = "middle";
    lines.forEach((l, i) => c.fillText(l, W / 2, y0 + 8 + lh * i + lh / 2 - 2));
  }

  private rysuj(d: Dane, k: Klatka, tex: Tekstura[]) {
    const gl = this.gl!,
      P = this.P!;
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.fbo);
    gl.viewport(0, 0, W, H);
    gl.clearColor(0, 0, 0, 1);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.enable(gl.BLEND);
    const nitki = new Map<number, Linia[]>();
    for (const l of k.l) nitki.set(l.i, [...(nitki.get(l.i) || []), l]);
    const u = P.spr.u;
    const wycinki = () => {
      gl.useProgram(P.spr.p);
      gl.bindVertexArray(this.vaoKw);
      gl.uniform2f(u.scr, W, H);
      gl.uniform3fv(u.shadowCol, SHADOW);
      gl.uniform3fv(u.hazeCol, HAZE);
      gl.activeTexture(gl.TEXTURE0);
      gl.uniform1i(u.tex, 0);
    };
    wycinki();
    const over = () => gl.blendFuncSeparate(gl.ONE, gl.ONE_MINUS_SRC_ALPHA, gl.ZERO, gl.ONE);
    const rysujNitki = (i: number) => {
      const ls = nitki.get(i);
      if (!ls) return;
      const v: number[] = [];
      for (const l of ls) {
        const h = l.w / 2;
        for (let j = 0; j + 3 < l.p.length; j += 2) {
          const [x0, y0, x1, y1] = [l.p[j], l.p[j + 1], l.p[j + 2], l.p[j + 3]];
          const n = Math.hypot(x1 - x0, y1 - y0) || 1,
            nx = (-(y1 - y0) / n) * h,
            ny = ((x1 - x0) / n) * h;
          for (const [x, y] of [
            [x0 + nx, y0 + ny],
            [x1 + nx, y1 + ny],
            [x0 - nx, y0 - ny],
            [x1 + nx, y1 + ny],
            [x1 - nx, y1 - ny],
            [x0 - nx, y0 - ny],
          ])
            v.push(x, y, l.c[0], l.c[1], l.c[2], l.a);
        }
      }
      gl.useProgram(P.lin.p);
      gl.uniform2f(P.lin.u.scr, W, H);
      gl.bindVertexArray(this.vaoLin);
      gl.bindBuffer(gl.ARRAY_BUFFER, this.linBuf);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(v), gl.STREAM_DRAW);
      over();
      gl.drawArrays(gl.TRIANGLES, 0, v.length / 6);
      wycinki();
    };
    k.e.forEach((e, i) => {
      rysujNitki(i);
      const [ti, Sx, Sy, kx, ky, rot, ax, ay, alpha, blur, sdx, sdy, soft, sila, tr, tg, tb, haze, mode] = e;
      const w = d.wycinki[ti];
      gl.bindTexture(gl.TEXTURE_2D, tex[ti].t);
      const rr = (rot * Math.PI) / 180;
      gl.uniform2f(u.S, Sx, Sy);
      gl.uniform2f(u.K, kx, ky);
      gl.uniform2f(u.R, Math.cos(rr), Math.sin(rr));
      gl.uniform2f(u.A, ax, ay);
      gl.uniform2f(u.size, w.w, w.h);
      gl.uniform2f(u.pxUV, 1 / (Math.abs(kx) * w.w), 1 / (Math.abs(ky) * w.h));
      gl.uniform1f(u.tpp, w.tw / (Math.max(Math.abs(kx), Math.abs(ky)) * w.w));
      if (sila > 0 && mode === 0) {
        const r = Math.hypot(soft, blur);
        gl.uniform1f(u.cien, 1);
        gl.uniform1f(u.sila, sila * alpha);
        gl.uniform1f(u.radius, r);
        gl.uniform1f(u.pad, 2.6 * r + 2);
        gl.uniform2f(u.off, sdx, sdy);
        over();
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      }
      gl.uniform1f(u.cien, 0);
      gl.uniform1f(u.radius, blur);
      gl.uniform1f(u.pad, 3 * blur + 2);
      gl.uniform2f(u.off, 0, 0);
      gl.uniform1f(u.alpha, alpha);
      gl.uniform1f(u.haze, haze);
      gl.uniform3f(u.tint, tr, tg, tb);
      gl.uniform1f(u.mode, mode);
      if (mode === 0) over();
      else if (mode === 1) gl.blendFuncSeparate(gl.ONE, gl.ONE, gl.ZERO, gl.ONE);
      else gl.blendFuncSeparate(gl.ZERO, gl.SRC_COLOR, gl.ZERO, gl.ONE);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    });
    rysujNitki(k.e.length);
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    gl.viewport(0, 0, W, H);
    gl.disable(gl.BLEND);
    gl.useProgram(P.post.p);
    gl.bindVertexArray(this.vaoKw);
    gl.bindTexture(gl.TEXTURE_2D, this.fboTex);
    gl.uniform1i(P.post.u.scena, 0);
    gl.uniform2f(P.post.u.scr, W, H);
    gl.uniform3fv(P.post.u.grade, k.gr);
    gl.uniform1f(P.post.u.dim, k.dim);
    gl.uniform1f(P.post.u.ziarno, k.ns % 997);
    gl.uniform4fv(P.post.u.spot, k.spot || [0, 0, 0, 0]);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  }
}

const TEATRY = new Map<string, Teatr>();
/** Teatr projektu (jeden na projekt i kartę przeglądarki) albo null, jeśli projekt nie ma ujęć rysowanych na żywo. */
export function teatrProjektu(project: Project): Teatr | null {
  if (!maTeatr(project)) return null;
  let t = TEATRY.get(project.id);
  if (!t) {
    t = new Teatr(project.id);
    TEATRY.set(project.id, t);
  }
  return t;
}
