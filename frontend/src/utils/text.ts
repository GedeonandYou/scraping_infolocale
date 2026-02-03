export function cleanText(s?: string | null): string {
  if (!s) return ""
  return String(s).replace(/\s+/g, " ").trim()
}

export function isNonEmptyString(x: unknown): x is string {
  return typeof x === "string" && x.trim().length > 0
}
