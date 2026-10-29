import { useEffect, useRef, useState } from "react";
import type { ReactNode, ButtonHTMLAttributes } from "react";
import type { LucideIcon } from "lucide-react";
import {
  X,
  Image as ImageIcon,
  Film,
  Music2,
  FileText,
  LoaderCircle,
} from "lucide-react";
import * as Dialog from "@radix-ui/react-dialog";
import type { Asset, Project } from "./types";
import { mediaUrl } from "./api";

export function Button({
  children,
  icon: Icon,
  primary = false,
  subtle = false,
  busy = false,
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  icon?: LucideIcon;
  primary?: boolean;
  subtle?: boolean;
  busy?: boolean;
}) {
  return (
    <button
      type="button"
      className={`button ${primary ? "primary" : ""} ${subtle ? "subtle" : ""} ${className}`}
      {...props}
      disabled={props.disabled || busy}
    >
      {busy ? (
        <LoaderCircle size={16} className="spin" />
      ) : Icon ? (
        <Icon size={16} />
      ) : null}
      {children}
    </button>
  );
}
export function IconButton({
  icon: Icon,
  label,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  icon: LucideIcon;
  label: string;
}) {
  return (
    <button
      type="button"
      className="icon-button"
      aria-label={label}
      title={label}
      {...props}
    >
      <Icon size={17} />
    </button>
  );
}
export function Modal({
  open,
  onClose,
  title,
  description,
  children,
  wide = false,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: ReactNode;
  wide?: boolean;
}) {
  return (
    <Dialog.Root open={open} onOpenChange={(value) => !value && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="modal-overlay" />
        <Dialog.Content className={`modal ${wide ? "wide" : ""}`}>
          <div className="modal-head">
            <div>
              <Dialog.Title>{title}</Dialog.Title>
              <Dialog.Description>
                {description || "DocOS Studio"}
              </Dialog.Description>
            </div>
            <Dialog.Close className="icon-button" aria-label="Zamknij">
              <X size={18} />
            </Dialog.Close>
          </div>
          <div className="modal-body">{children}</div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
export function Field({
  label,
  children,
  hint,
}: {
  label: string;
  children: ReactNode;
  hint?: string;
}) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      {children}
      {hint && <span className="field-hint">{hint}</span>}
    </label>
  );
}
export function CommitText({
  value,
  onCommit,
  multiline = false,
  rows = 3,
  placeholder = "",
  className = "",
  disabled = false,
  label,
}: {
  value: string;
  onCommit: (v: string) => void;
  multiline?: boolean;
  rows?: number;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
  label?: string;
}) {
  const [v, setV] = useState(value);
  const focused = useRef(false);
  const pending = useRef<ReturnType<typeof setTimeout> | undefined>(undefined),
    raw = useRef(value),
    sent = useRef(value),
    commit = useRef(onCommit);
  commit.current = onCommit;
  function flush() {
    clearTimeout(pending.current);
    window.dispatchEvent(new CustomEvent("docos:dirty", { detail: false }));
    if (raw.current !== sent.current) {
      sent.current = raw.current;
      commit.current(raw.current);
    }
  }
  useEffect(
    () => () => {
      clearTimeout(pending.current);
      window.dispatchEvent(new CustomEvent("docos:dirty", { detail: false }));
      if (raw.current !== sent.current) {
        sent.current = raw.current;
        commit.current(raw.current);
      }
    },
    [],
  );
  useEffect(() => {
    if (!focused.current) {
      setV(value);
      raw.current = value;
      sent.current = value;
    }
  }, [value]);
  const props = {
    "aria-label": label,
    value: v,
    placeholder,
    className,
    disabled,
    onFocus: () => {
      focused.current = true;
    },
    onChange: (
      e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
    ) => {
      setV(e.target.value);
      window.dispatchEvent(new CustomEvent("docos:dirty", { detail: true }));
      raw.current = e.target.value;
      clearTimeout(pending.current);
      pending.current = setTimeout(flush, 900);
    },
    onBlur: () => {
      focused.current = false;
      flush();
    },
  };
  return multiline ? <textarea {...props} rows={rows} /> : <input {...props} />;
}
export function NumberField({
  label,
  value,
  onCommit,
  min = 0,
  max = 100000,
  step = 0.1,
  disabled = false,
}: {
  label: string;
  value: number;
  onCommit: (v: number) => void;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
}) {
  const [v, setV] = useState(String(Math.round(value * 1000) / 1000));
  const focused = useRef(false);
  useEffect(() => {
    if (!focused.current) setV(String(Math.round(value * 1000) / 1000));
  }, [value]);
  return (
    <Field label={label}>
      <input
        type="number"
        value={v}
        min={min}
        max={max}
        step={step}
        disabled={disabled}
        onFocus={() => {
          focused.current = true;
        }}
        onChange={(e) => setV(e.target.value)}
        onBlur={() => {
          focused.current = false;
          const n = Number(v);
          if (Number.isFinite(n) && n >= min && n <= max) {
            if (n !== value) onCommit(n);
          } else setV(String(value));
        }}
      />
    </Field>
  );
}
export function AssetThumb({
  asset,
  project,
  large = false,
}: {
  asset?: Asset;
  project: Project;
  large?: boolean;
}) {
  const Icon =
    asset?.kind === "video"
      ? Film
      : asset?.kind === "audio"
        ? Music2
        : asset?.kind === "document"
          ? FileText
          : ImageIcon;
  return (
    <div className={`asset-thumb ${large ? "large" : ""}`}>
      {asset && (asset.thumbnail || asset.kind === "image") ? (
        <img
          src={mediaUrl(project.id, asset.id, !!asset.thumbnail)}
          alt={asset.name}
          loading="lazy"
        />
      ) : (
        <Icon size={large ? 32 : 20} />
      )}{" "}
      {asset?.kind === "video" && (
        <span className="media-type">
          <Film size={12} />
        </span>
      )}
    </div>
  );
}
export function Empty({
  icon: Icon = FileText,
  title,
  children,
  action,
}: {
  icon?: LucideIcon;
  title: string;
  children?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="empty-state">
      <span className="empty-icon">
        <Icon size={26} />
      </span>
      <h3>{title}</h3>
      {children && <p>{children}</p>}
      {action}
    </div>
  );
}
export function SectionHead({
  eyebrow,
  title,
  description,
  children,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  children?: ReactNode;
}) {
  return (
    <div className="section-head">
      <div>
        {eyebrow && <div className="eyebrow">{eyebrow}</div>}
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      <div className="head-actions">{children}</div>
    </div>
  );
}
