export async function api<T>(
  path: string,
  body?: unknown,
  method = body === undefined ? "GET" : "POST",
): Promise<T> {
  const response = await fetch(
    "/api" + path,
    method === "GET"
      ? undefined
      : {
          method,
          headers: {
            "Content-Type": "application/json",
            "X-Docos-Request": "1",
          },
          body: body === undefined ? undefined : JSON.stringify(body),
        },
  );
  if (!response.ok) {
    let message = `Błąd ${response.status}`;
    try {
      const data = await response.json();
      message =
        typeof data.detail === "string"
          ? data.detail
          : JSON.stringify(data.detail);
    } catch {
      /* non-JSON upstream */
    }
    throw Object.assign(new Error(message), { status: response.status });
  }
  return response.json();
}
export async function download(path: string, name: string) {
  const response = await fetch("/api" + path);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Nie udało się przygotować pliku");
  }
  const url = URL.createObjectURL(await response.blob()),
    a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export async function upload<T>(path: string, file: File): Promise<T> {
  const data = new FormData();
  data.append("file", file);
  const response = await fetch("/api" + path, {
    method: "POST",
    headers: { "X-Docos-Request": "1" },
    body: data,
  });
  if (!response.ok) {
    const data = await response.json();
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Nie udało się wczytać pliku",
    );
  }
  return response.json();
}
export const mediaUrl = (project: string, asset: string, thumbnail = false) =>
  `/api/projects/${project}/media/${asset}${thumbnail ? "?thumbnail=true" : ""}`;
export const id = (prefix: string) =>
  prefix + crypto.randomUUID().replaceAll("-", "").slice(0, 16);
export const safeUrl = (value: string | undefined) => {
  try {
    const u = new URL(value || "");
    return ["https:", "http:"].includes(u.protocol) ? u.href : undefined;
  } catch {
    return undefined;
  }
};
export function saveText(name: string, content: string, type = "text/plain") {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
