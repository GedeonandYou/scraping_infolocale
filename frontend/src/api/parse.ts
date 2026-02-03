export function extractArray<T = unknown>(data: unknown, keys: string[]): T[] {
  if (Array.isArray(data)) return data as T[]
  if (data && typeof data === "object") {
    const obj = data as Record<string, unknown>
    for (const k of keys) {
      if (Array.isArray(obj[k])) return obj[k] as T[]
    }
  }
  return []
}

export function extractObject(data: unknown, keys: string[]): unknown | null {
  if (data && typeof data === "object" && !Array.isArray(data)) {
    const obj = data as Record<string, unknown>
    for (const k of keys) {
      if (obj[k] && typeof obj[k] === "object") return obj[k]
    }
    return data
  }
  return null
}

export function normalizeName(item: unknown): string {
  if (typeof item === "string") return item.trim()
  if (item && typeof item === "object") {
    const obj = item as Record<string, unknown>
    const candidate =
      obj.name ?? obj.label ?? obj.title ?? obj.value ?? obj.city ?? obj.category
    if (typeof candidate === "string") return candidate.trim()
  }
  return ""
}

export function extractTotalFromHeaders(headers: Headers): number | null {
  const xTotal = headers.get("x-total-count")
  if (xTotal) {
    const n = Number.parseInt(xTotal, 10)
    if (Number.isFinite(n)) return n
  }

  const contentRange = headers.get("content-range")
  if (contentRange) {
    const match = contentRange.match(/\/(\d+)\s*$/)
    if (match?.[1]) {
      const n = Number.parseInt(match[1], 10)
      if (Number.isFinite(n)) return n
    }
  }
  return null
}

export function extractTotalFromBody(data: unknown): number | null {
  if (!data || typeof data !== "object") return null
  const obj = data as Record<string, unknown>

  const direct = obj.count ?? obj.total
  if (typeof direct === "number") return direct

  const meta = obj.meta
  if (meta && typeof meta === "object") {
    const m = meta as Record<string, unknown>
    if (typeof m.total === "number") return m.total
    if (typeof m.count === "number") return m.count
  }
  return null
}
