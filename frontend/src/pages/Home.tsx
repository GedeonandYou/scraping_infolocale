import { EventDetailSheet } from "@/components/EventDetailSheet"
import { EventsTable } from "@/components/EventsTable"
import { FilterBar } from "@/components/FilterBar"
import { LogsPanel } from "@/components/LogsPanel"
import { StatsCard } from "@/components/StatsCard"
import {
  mockLogs,
  type ApiEvent,
  type ScannedEvent,
  mapApiEventToScannedEvent,
} from "@/data/Events"
import { Activity, Calendar, Database, MapPin } from "lucide-react"
import { useEffect, useMemo, useRef, useState } from "react"

const API_URL = "http://localhost:8000/api/v1"

/** Helpers */
function extractArray(data: unknown, keys: string[]): unknown[] {
  if (Array.isArray(data)) return data
  if (data && typeof data === "object") {
    const obj = data as Record<string, unknown>
    for (const k of keys) {
      if (Array.isArray(obj[k])) return obj[k] as unknown[]
    }
  }
  return []
}

function extractObject(data: unknown, keys: string[]): unknown | null {
  if (data && typeof data === "object" && !Array.isArray(data)) {
    const obj = data as Record<string, unknown>
    for (const k of keys) {
      if (obj[k] && typeof obj[k] === "object") return obj[k]
    }
    return data
  }
  return null
}

function normalizeName(item: unknown): string {
  if (typeof item === "string") return item.trim()
  if (item && typeof item === "object") {
    const obj = item as Record<string, unknown>
    const candidate = obj.name ?? obj.label ?? obj.title ?? obj.value ?? obj.city ?? obj.category
    if (typeof candidate === "string") return candidate.trim()
  }
  return ""
}

function extractTotalFromHeaders(headers: Headers): number | null {
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

function extractTotalFromBody(data: unknown): number | null {
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

export default function Home() {
  const [events, setEvents] = useState<ScannedEvent[]>([])
  const [eventsCount, setEventsCount] = useState<number>(0)
  const [eventsLoading, setEventsLoading] = useState(true)
  const [eventsError, setEventsError] = useState<string | null>(null)

  const [categories, setCategories] = useState<string[]>([])
  const [cities, setCities] = useState<string[]>([])
  const [catsLoading, setCatsLoading] = useState(true)
  const [citiesLoading, setCitiesLoading] = useState(true)

  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [selectedCity, setSelectedCity] = useState<string | null>(null)

  // ✅ détail
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null)
  const [selectedEvent, setSelectedEvent] = useState<ScannedEvent | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState<string | null>(null)
  const cacheRef = useRef<Map<string, ScannedEvent>>(new Map())

  /** Fetch list events */
  useEffect(() => {
    const controller = new AbortController()

    const run = async () => {
      try {
        setEventsLoading(true)
        setEventsError(null)

        const url = `${API_URL}/events`
        console.log("🔄 Fetching from:", url)

        const res = await fetch(url, {
          headers: { "Content-Type": "application/json" },
          signal: controller.signal,
        })

        console.log("📡 Response status:", res.status)

        if (!res.ok) throw new Error(`Erreur API events: ${res.status} - ${res.statusText}`)

        const totalFromHeaders = extractTotalFromHeaders(res.headers)
        const data: unknown = await res.json()

        const raw = extractArray(data, ["data", "events", "results"])
        const mapped = raw.map((x) => mapApiEventToScannedEvent(x as ApiEvent))

        const totalFromBody = extractTotalFromBody(data)
        const total = totalFromHeaders ?? totalFromBody ?? mapped.length

        console.log("✅ Final events array length:", mapped.length)
        console.log("✅ Total events (computed):", total)

        setEvents(mapped)
        setEventsCount(total)
      } catch (e) {
        if (e instanceof DOMException && e.name === "AbortError") return
        setEventsError(e instanceof Error ? e.message : "Erreur inconnue")
      } finally {
        setEventsLoading(false)
      }
    }

    run()
    return () => controller.abort()
  }, [])

  /** Fetch categories */
  useEffect(() => {
    const controller = new AbortController()

    const run = async () => {
      try {
        setCatsLoading(true)
        const res = await fetch(`${API_URL}/categories`, {
          headers: { "Content-Type": "application/json" },
          signal: controller.signal,
        })
        if (!res.ok) throw new Error(`Erreur API categories: ${res.status}`)

        const data: unknown = await res.json()
        const raw = extractArray(data, ["data", "categories", "results"])
        const names = raw.map(normalizeName).filter(Boolean)
        setCategories(Array.from(new Set(names)).sort((a, b) => a.localeCompare(b, "fr")))
      } catch {
        setCategories([])
      } finally {
        setCatsLoading(false)
      }
    }

    run()
    return () => controller.abort()
  }, [])

  /** Fetch cities */
  useEffect(() => {
    const controller = new AbortController()

    const run = async () => {
      try {
        setCitiesLoading(true)
        const res = await fetch(`${API_URL}/cities`, {
          headers: { "Content-Type": "application/json" },
          signal: controller.signal,
        })
        if (!res.ok) throw new Error(`Erreur API cities: ${res.status}`)

        const data: unknown = await res.json()
        const raw = extractArray(data, ["data", "cities", "results"])
        const names = raw.map(normalizeName).filter(Boolean)
        setCities(Array.from(new Set(names)).sort((a, b) => a.localeCompare(b, "fr")))
      } catch {
        setCities([])
      } finally {
        setCitiesLoading(false)
      }
    }

    run()
    return () => controller.abort()
  }, [])

  /** Fetch detail /events/{id} */
  useEffect(() => {
    if (!selectedEventId) return
    const controller = new AbortController()

    const run = async () => {
      try {
        setDetailLoading(true)
        setDetailError(null)

        const cached = cacheRef.current.get(selectedEventId)
        if (cached) {
          setSelectedEvent(cached)
          setDetailLoading(false)
          return
        }

        const url = `${API_URL}/events/${encodeURIComponent(selectedEventId)}`
        console.log("🔎 Fetching event detail:", url)

        const res = await fetch(url, {
          headers: { "Content-Type": "application/json" },
          signal: controller.signal,
        })

        if (!res.ok) throw new Error(`Erreur API event detail: ${res.status} - ${res.statusText}`)

        const data: unknown = await res.json()
        const obj = extractObject(data, ["data", "event", "result"]) ?? data

        const mapped = mapApiEventToScannedEvent(obj as ApiEvent)
        cacheRef.current.set(selectedEventId, mapped)
        setSelectedEvent(mapped)
      } catch (e) {
        if (e instanceof DOMException && e.name === "AbortError") return
        setDetailError(e instanceof Error ? e.message : "Erreur inconnue")
      } finally {
        setDetailLoading(false)
      }
    }

    run()
    return () => controller.abort()
  }, [selectedEventId])

  const filteredEvents = useMemo(() => {
    const q = searchQuery.trim().toLowerCase()

    return events.filter((event) => {
      const matchesSearch =
        !q ||
        (event.title ?? "").toLowerCase().includes(q) ||
        (event.description ?? "").toLowerCase().includes(q) ||
        (event.organizer ?? "").toLowerCase().includes(q)

      const matchesCategory = !selectedCategory || event.category === selectedCategory
      const matchesCity = !selectedCity || event.city === selectedCity

      return matchesSearch && matchesCategory && matchesCity
    })
  }, [events, searchQuery, selectedCategory, selectedCity])

  const lastUpdateLabel = useMemo(() => {
    return new Date().toLocaleDateString("fr-FR", { day: "2-digit", month: "long", year: "numeric" })
  }, [])

  const onSelect = (e: ScannedEvent) => {
    setSelectedEvent(e) // aperçu rapide
    setSelectedEventId(String(e.id))
  }

  const closeSheet = () => {
    setSelectedEventId(null)
    setSelectedEvent(null)
    setDetailError(null)
    setDetailLoading(false)
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary rounded-lg">
              <Database className="h-5 w-5 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Infolocale Scraper</h1>
              <p className="text-sm text-muted-foreground">Dashboard de collecte d&apos;événements</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatsCard title="Événements collectés" value={eventsLoading ? "..." : eventsCount} subtitle="Total en base" icon={Calendar} />
          <StatsCard title="Villes" value={citiesLoading ? "..." : cities.length} subtitle="Depuis /cities" icon={MapPin} />
          <StatsCard title="Catégories" value={catsLoading ? "..." : categories.length} subtitle="Depuis /categories" icon={Activity} />
          <StatsCard title="Dernière MAJ" value={eventsLoading ? "..." : "Chargée"} subtitle={lastUpdateLabel} icon={Database} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <div>
              <h2 className="text-lg font-semibold mb-4">Événements récents</h2>

              <FilterBar
                searchQuery={searchQuery}
                onSearchChange={setSearchQuery}
                selectedCategory={selectedCategory}
                onCategoryChange={setSelectedCategory}
                selectedCity={selectedCity}
                onCityChange={setSelectedCity}
                categories={categories}
                cities={cities}
                categoriesLoading={catsLoading}
                citiesLoading={citiesLoading}
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-4">
                {eventsError ? (
                  <p className="text-sm text-red-600">❌ Erreur: {eventsError}</p>
                ) : eventsLoading ? (
                  <p className="text-sm text-muted-foreground">⏳ Chargement des événements...</p>
                ) : (
                  <p className="text-sm text-muted-foreground">
                    {filteredEvents.length} événement{filteredEvents.length > 1 ? "s" : ""} trouvé{filteredEvents.length > 1 ? "s" : ""}
                  </p>
                )}
              </div>

              {!eventsLoading && !eventsError ? (
                <EventsTable events={filteredEvents} onSelectEvent={onSelect} />
              ) : null}
            </div>
          </div>

          <div className="space-y-6">
            <LogsPanel logs={mockLogs} />
          </div>
        </div>
      </main>

      <EventDetailSheet
        event={selectedEvent}
        open={!!selectedEventId}
        onClose={closeSheet}
        loading={detailLoading}
        error={detailError}
      />
    </div>
  )
}
