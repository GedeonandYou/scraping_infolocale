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

function safeString(v: unknown): string {
  return typeof v === "string" ? v : ""
}
function safeNumber(v: unknown): number | undefined {
  return typeof v === "number" && Number.isFinite(v) ? v : undefined
}

export function mapApiEventToScannedEvent(api: ApiEvent): ScannedEvent {
  return {
    id: safeNumber(api.id) ?? 0,
    uid: safeString(api.uid),

    title: safeString(api.title),
    category: safeString(api.category),

    beginDate: safeString(api.begin_date),
    endDate: api.end_date ?? undefined,
    startTime: api.start_time ?? undefined,
    endTime: api.end_time ?? undefined,

    description: safeString(api.description),
    organizer: safeString(api.organizer),
    pricing: api.pricing ?? undefined,
    website: api.website ?? undefined,

    tags: Array.isArray(api.tags) ? api.tags : [],
    artists: Array.isArray(api.artists) ? api.artists : undefined,
    sponsors: Array.isArray(api.sponsors) ? api.sponsors : undefined,

    locationName: safeString(api.location_name),
    address: safeString(api.address),
    zipcode: safeString(api.zipcode),
    city: safeString(api.city),
    state: safeString(api.state),
    country: safeString(api.country),

    latitude: safeNumber(api.latitude),
    longitude: safeNumber(api.longitude),

    displayName: api.display_name ?? undefined,
    placeId: api.place_id ?? undefined,
    placeName: api.place_name ?? undefined,
    placeTypes: Array.isArray(api.place_types) ? api.place_types : undefined,

    rating: safeNumber(api.rating),
    imagePath: api.image_path ?? undefined,
    qrCode: api.qr_code ?? undefined,
    schemaOrgTypes: Array.isArray(api.schema_org_types) ? api.schema_org_types : undefined,
    rawJson: api.raw_json ?? undefined,

    createdAt: api.created_at ?? undefined,
    isPrivate: api.is_private ?? undefined,
    userId: safeNumber(api.user_id),
  }
}

/* --- tes mocks peuvent rester (inchangés) --- */
export const mockLogs = [
  { time: "10:15", message: "Scraping démarré", level: "info" as const },
  { time: "10:17", message: "20 événements récupérés", level: "success" as const },
  { time: "10:18", message: "1 doublon ignoré", level: "warning" as const },
  { time: "10:19", message: "Scraping terminé", level: "success" as const },
]

export const mockEvents: ScannedEvent[] = []
