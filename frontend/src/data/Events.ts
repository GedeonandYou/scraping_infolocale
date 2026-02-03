// src/data/Events.ts

export interface ApiEvent {
  title?: string | null
  category?: string | null

  begin_date?: string | null
  end_date?: string | null
  start_time?: string | null
  end_time?: string | null

  description?: string | null
  organizer?: string | null
  pricing?: string | null
  website?: string | null

  tags?: string[] | null
  artists?: string[] | null
  sponsors?: string[] | null

  location_name?: string | null
  address?: string | null
  zipcode?: string | null
  city?: string | null
  state?: string | null
  country?: string | null

  latitude?: number | null
  longitude?: number | null

  display_name?: string | null
  place_id?: string | null
  place_name?: string | null
  place_types?: string[] | null

  rating?: number | null
  image_path?: string | null
  qr_code?: string | null
  schema_org_types?: string[] | null
  raw_json?: Record<string, unknown> | null

  is_private?: boolean | null
  id?: number | null
  uid?: string | null
  user_id?: number | null
  created_at?: string | null
}

export interface ScannedEvent {
  id: number
  uid: string

  title: string
  category: string

  beginDate: string
  endDate?: string
  startTime?: string
  endTime?: string

  description: string
  organizer: string
  pricing?: string
  website?: string

  tags: string[]
  artists?: string[]
  sponsors?: string[]

  locationName: string
  address: string
  zipcode: string
  city: string
  state: string
  country: string

  latitude?: number
  longitude?: number

  // extras (optionnels)
  displayName?: string
  placeId?: string
  placeName?: string
  placeTypes?: string[]
  rating?: number
  imagePath?: string
  qrCode?: string
  schemaOrgTypes?: string[]
  rawJson?: Record<string, unknown>

  createdAt?: string
  isPrivate?: boolean
  userId?: number
}

/** ---------- helpers safe parsing ---------- */

function asTrimmedString(v: unknown): string {
  return typeof v === "string" ? v.trim() : ""
}

function asOptionalTrimmedString(v: unknown): string | undefined {
  const s = typeof v === "string" ? v.trim() : ""
  return s.length > 0 ? s : undefined
}

function asFiniteNumber(v: unknown): number | undefined {
  return typeof v === "number" && Number.isFinite(v) ? v : undefined
}

function asStringArray(v: unknown): string[] {
  if (!Array.isArray(v)) return []
  return v
    .filter((x): x is string => typeof x === "string")
    .map((s) => s.trim())
    .filter((s) => s.length > 0)
}

/** ---------- mapper API -> UI ---------- */

export function mapApiEventToScannedEvent(api: ApiEvent): ScannedEvent {
  const id = asFiniteNumber(api.id) ?? 0

  return {
    id,
    uid: asTrimmedString(api.uid),

    title: asTrimmedString(api.title),
    category: asTrimmedString(api.category),

    beginDate: asTrimmedString(api.begin_date),
    endDate: asOptionalTrimmedString(api.end_date),
    startTime: asOptionalTrimmedString(api.start_time),
    endTime: asOptionalTrimmedString(api.end_time),

    description: asTrimmedString(api.description),
    organizer: asTrimmedString(api.organizer),
    pricing: asOptionalTrimmedString(api.pricing),
    website: asOptionalTrimmedString(api.website),

    tags: asStringArray(api.tags),
    artists: asStringArray(api.artists).length ? asStringArray(api.artists) : undefined,
    sponsors: asStringArray(api.sponsors).length ? asStringArray(api.sponsors) : undefined,

    locationName: asTrimmedString(api.location_name),
    address: asTrimmedString(api.address),
    zipcode: asTrimmedString(api.zipcode),
    city: asTrimmedString(api.city),
    state: asTrimmedString(api.state),
    country: asTrimmedString(api.country),

    latitude: asFiniteNumber(api.latitude),
    longitude: asFiniteNumber(api.longitude),

    displayName: asOptionalTrimmedString(api.display_name),
    placeId: asOptionalTrimmedString(api.place_id),
    placeName: asOptionalTrimmedString(api.place_name),
    placeTypes: asStringArray(api.place_types).length
      ? asStringArray(api.place_types)
      : undefined,

    rating: asFiniteNumber(api.rating),
    imagePath: asOptionalTrimmedString(api.image_path),
    qrCode: asOptionalTrimmedString(api.qr_code),
    schemaOrgTypes: asStringArray(api.schema_org_types).length
      ? asStringArray(api.schema_org_types)
      : undefined,
    rawJson: api.raw_json ?? undefined,

    createdAt: asOptionalTrimmedString(api.created_at),
    isPrivate: typeof api.is_private === "boolean" ? api.is_private : undefined,
    userId: asFiniteNumber(api.user_id),
  }
}

/** ---------- mocks (optionnels) ---------- */

export type LogLevel = "info" | "success" | "warning" | "error"

export interface LogItem {
  time: string
  message: string
  level: LogLevel
}

export const mockLogs: LogItem[] = [
  { time: "10:15", message: "Scraping démarré", level: "info" },
  { time: "10:17", message: "20 événements récupérés", level: "success" },
  { time: "10:18", message: "1 doublon ignoré", level: "warning" },
  { time: "10:19", message: "Scraping terminé", level: "success" },
]

export const mockEvents: ScannedEvent[] = []
