import { Fragment, type ReactNode } from "react";

/** Mały, bezpieczny renderer Markdown (bez HTML): nagłówki, akapity, listy, tabele, kod, pogrubienia, linki. */
function inline(text: string, key: string): ReactNode[] {
  const out: ReactNode[] = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))/g;
  let last = 0, m: RegExpExecArray | null, i = 0;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(text.slice(last, m.index));
    const t = m[0];
    if (t.startsWith("**")) out.push(<strong key={key + i++}>{t.slice(2, -2)}</strong>);
    else if (t.startsWith("`")) out.push(<code key={key + i++}>{t.slice(1, -1)}</code>);
    else {
      const [, label, href] = /\[([^\]]+)\]\(([^)]+)\)/.exec(t) || [];
      out.push(/^https?:/.test(href || "") ? <a key={key + i++} href={href} target="_blank" rel="noreferrer">{label}</a>
        : <span key={key + i++} className="md-ref" title={href}>{label}</span>);
    }
    last = m.index + t.length;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}

export default function Markdown({ text }: { text: string }) {
  const lines = (text || "").replace(/\r/g, "").split("\n");
  const blocks: ReactNode[] = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (!line.trim()) { i++; continue; }
    if (line.startsWith("```")) {
      const body: string[] = [];
      for (i++; i < lines.length && !lines[i].startsWith("```"); i++) body.push(lines[i]);
      i++;
      blocks.push(<pre key={i}><code>{body.join("\n")}</code></pre>);
      continue;
    }
    const h = /^(#{1,4})\s+(.*)$/.exec(line);
    if (h) {
      const level = h[1].length, content = inline(h[2], "h" + i);
      blocks.push(level === 1 ? <h2 key={i}>{content}</h2> : level === 2 ? <h3 key={i}>{content}</h3> : <h4 key={i}>{content}</h4>);
      i++;
      continue;
    }
    if (line.trim().startsWith("|")) {
      const rows: string[][] = [];
      for (; i < lines.length && lines[i].trim().startsWith("|"); i++) {
        const cells = lines[i].trim().replace(/^\||\|$/g, "").split("|").map(c => c.trim());
        if (!cells.every(c => /^:?-{2,}:?$/.test(c))) rows.push(cells);
      }
      const [head, ...body] = rows;
      blocks.push(<div className="md-table" key={i}><table>
        <thead><tr>{head.map((c, k) => <th key={k}>{inline(c, `th${i}${k}`)}</th>)}</tr></thead>
        <tbody>{body.map((r, n) => <tr key={n}>{r.map((c, k) => <td key={k}>{inline(c, `td${i}${n}${k}`)}</td>)}</tr>)}</tbody>
      </table></div>);
      continue;
    }
    if (/^\s*([-*]|\d+\.)\s+/.test(line)) {
      const ordered = /^\s*\d+\./.test(line), items: string[] = [];
      for (; i < lines.length && /^\s*([-*]|\d+\.)\s+/.test(lines[i]); i++) {
        let item = lines[i].replace(/^\s*([-*]|\d+\.)\s+/, "");
        while (i + 1 < lines.length && /^\s{2,}\S/.test(lines[i + 1]) && !/^\s*([-*]|\d+\.)\s+/.test(lines[i + 1])) item += " " + lines[++i].trim();
        items.push(item);
      }
      const li = items.map((t, k) => <li key={k}>{inline(t, `li${i}${k}`)}</li>);
      blocks.push(ordered ? <ol key={i}>{li}</ol> : <ul key={i}>{li}</ul>);
      continue;
    }
    const para: string[] = [];
    for (; i < lines.length && lines[i].trim() && !/^(#{1,4}\s|```|\s*\||\s*([-*]|\d+\.)\s)/.test(lines[i]); i++) para.push(lines[i].trim());
    if (!para.length) { para.push(line); i++; }
    blocks.push(<p key={i}>{inline(para.join(" "), "p" + i)}</p>);
  }
  return <div className="markdown">{blocks.map((b, k) => <Fragment key={k}>{b}</Fragment>)}</div>;
}
