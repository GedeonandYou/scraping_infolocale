import { API_URL } from "./config"
import {
  extractArray,
  extractObject,
  extractTotalFromBody,
  extractTotalFromHeaders,
  normalizeName,
} from "./parse"
import {
  mapApiEventToScannedEvent,
  type ApiEvent,
  type ScannedEvent,
} from "@/data/Events"

async function fetchJson(path: string, signal?: AbortSignal) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    signal,
  })
  if (!res.ok) throw new Error(`API ${path}: ${res.status} - ${res.statusText}`)
  const data: unknown = await res.json()
  return { data, headers: res.headers }
}

export async function fetchEvents(signal?: AbortSignal): Promise<{
  events: ScannedEvent[]
  total: number
}> {
  const { data, headers } = await fetchJson("/events", signal)

  const raw = extractArray<ApiEvent>(data, ["data", "events", "results"])
  const mapped = raw.map(mapApiEventToScannedEvent)

  const total =
    extractTotalFromHeaders(headers) ??
    extractTotalFromBody(data) ??
    mapped.length

  return { events: mapped, total }
}

export async function fetchEventDetail(
  id: string,
  signal?: AbortSignal,
): Promise<ScannedEvent> {
  const { data } = await fetchJson(`/events/${encodeURIComponent(id)}`, signal)
  const obj = extractObject(data, ["data", "event", "result"]) ?? data
  return mapApiEventToScannedEvent(obj as ApiEvent)
}

export async function fetchCategories(signal?: AbortSignal): Promise<string[]> {
  const { data } = await fetchJson("/categories", signal)
  const raw = extractArray<unknown>(data, ["data", "categories", "results"])
  const names = raw.map(normalizeName).filter(Boolean)
  return Array.from(new Set(names)).sort((a, b) => a.localeCompare(b, "fr"))
}

export async function fetchCities(signal?: AbortSignal): Promise<string[]> {
  const { data } = await fetchJson("/cities", signal)
  const raw = extractArray<unknown>(data, ["data", "cities", "results"])
  const names = raw.map(normalizeName).filter(Boolean)
  return Array.from(new Set(names)).sort((a, b) => a.localeCompare(b, "fr"))
}
