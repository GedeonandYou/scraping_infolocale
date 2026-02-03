import { EventDetailSheet } from "@/components/EventDetailSheet"
import { EventsTable } from "@/components/EventsTable"
import { FilterBar } from "@/components/FilterBar"
import { LogsPanel } from "@/components/LogsPanel"
import { StatsCard } from "@/components/StatsCard"
import { mockLogs, type ScannedEvent } from "@/data/Events"
import { useCategories } from "@/hooks/useCategories"
import { useCities } from "@/hooks/useCities"
import { useEventDetail } from "@/hooks/useEventDetail"
import { useEventsList } from "@/hooks/useEventsList"
import { Activity, Calendar, Database, MapPin } from "lucide-react"
import { useMemo, useState } from "react"

export default function Home() {
  // ✅ data
  const { events, total, loading: eventsLoading, error: eventsError } =
    useEventsList()
  const { categories, loading: catsLoading } = useCategories()
  const { cities, loading: citiesLoading } = useCities()

  // ✅ detail sheet (avec cache)
  const detail = useEventDetail()

  // ✅ filtres UI
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [selectedCity, setSelectedCity] = useState<string | null>(null)

  const filteredEvents = useMemo(() => {
    const q = searchQuery.trim().toLowerCase()

    return events.filter((event) => {
      const matchesSearch =
        !q ||
        event.title.toLowerCase().includes(q) ||
        event.description.toLowerCase().includes(q) ||
        event.organizer.toLowerCase().includes(q)

      const matchesCategory =
        !selectedCategory || event.category === selectedCategory
      const matchesCity = !selectedCity || event.city === selectedCity

      return matchesSearch && matchesCategory && matchesCity
    })
  }, [events, searchQuery, selectedCategory, selectedCity])

  const lastUpdateLabel = useMemo(() => {
    return new Date().toLocaleDateString("fr-FR", {
      day: "2-digit",
      month: "long",
      year: "numeric",
    })
  }, [])

  const onSelect = (e: ScannedEvent) => detail.open(e)

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
              <p className="text-sm text-muted-foreground">
                Dashboard de collecte d&apos;événements
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatsCard
            title="Événements collectés"
            value={eventsLoading ? "..." : total}
            subtitle="Total en base"
            icon={Calendar}
          />
          <StatsCard
            title="Villes"
            value={citiesLoading ? "..." : cities.length}
            subtitle="Depuis /cities"
            icon={MapPin}
          />
          <StatsCard
            title="Catégories"
            value={catsLoading ? "..." : categories.length}
            subtitle="Depuis /categories"
            icon={Activity}
          />
          <StatsCard
            title="Dernière MAJ"
            value={eventsLoading ? "..." : "Chargée"}
            subtitle={lastUpdateLabel}
            icon={Database}
          />
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
                  <p className="text-sm text-muted-foreground">
                    ⏳ Chargement des événements...
                  </p>
                ) : (
                  <p className="text-sm text-muted-foreground">
                    {filteredEvents.length} événement
                    {filteredEvents.length > 1 ? "s" : ""} trouvé
                    {filteredEvents.length > 1 ? "s" : ""}
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
        event={detail.event}
        open={detail.isOpen}
        onClose={detail.close}
        loading={detail.loading}
        error={detail.error}
      />
    </div>
  )
}
