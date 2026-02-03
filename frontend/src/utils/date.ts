function safeDate(dateString?: string | null): Date | null {
  if (!dateString) return null
  const d = new Date(dateString)
  return Number.isNaN(d.getTime()) ? null : d
}

export function formatFullDate(dateString?: string | null): string {
  const d = safeDate(dateString)
  if (!d) return "—"
  return d.toLocaleDateString("fr-FR", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  })
}

export function formatShortDate(dateString?: string | null): string {
  const d = safeDate(dateString)
  if (!d) return "—"
  return d.toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "short",
    year: "numeric",
  })
}
