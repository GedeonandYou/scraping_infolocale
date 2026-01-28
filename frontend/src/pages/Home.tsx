import { EventDetailSheet } from "@/components/EventDetailSheet"
import { EventsTable } from "@/components/EventsTable"
import { FilterBar } from "@/components/FilterBar"
import { LogsPanel } from "@/components/LogsPanel"
import { StatsCard } from "@/components/StatsCard"
import { mockEvents, mockLogs, type ScannedEvent } from "@/data/Events"
import { Activity, Calendar, Database, MapPin } from "lucide-react"
import { useMemo, useState } from "react"

export default function Home() {
  /**
   * ! STATE (état, données) de l'application
   */
  const [selectedEvent, setSelectedEvent] = useState<ScannedEvent | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [selectedCity, setSelectedCity] = useState<string | null>(null)

  /**
   * ! COMPORTEMENT (méthodes, fonctions) de l'application
   */

  const filteredEvents = useMemo(() => {
    return mockEvents.filter((event) => {
      const matchesSearch =
        !searchQuery ||
        event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        event.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        event.organizer.toLowerCase().includes(searchQuery.toLowerCase())

      const matchesCategory =
        !selectedCategory || event.category === selectedCategory
      const matchesCity = !selectedCity || event.city === selectedCity

      return matchesSearch && matchesCategory && matchesCity
    })
  }, [searchQuery, selectedCategory, selectedCity])

  const uniqueCities = new Set(mockEvents.map((e) => e.city)).size
  const uniqueCategories = new Set(mockEvents.map((e) => e.category)).size

  /**
   * ! AFFICHAGE (render) de l'application
   */
  return (
    <>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="border-b border-border bg-card/80 backdrop-blur-sm sticky top-0 z-50">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary rounded-lg">
                  <Database className="h-5 w-5 text-primary-foreground" />
                </div>
                <div>
                  <h1 className="text-xl font-bold">Infolocale Scraper</h1>
                  <p className="text-sm text-muted-foreground">
                    Dashboard de collecte d'événements
                  </p>
                </div>
              </div>
            </div>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8">

          {/* Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <StatsCard
              title="Événements collectés"
              value={mockEvents.length}
              subtitle="Total en base"
              icon={Calendar}
            />
            <StatsCard
              title="Villes couvertes"
              value={uniqueCities}
              subtitle="Bretagne & Pays de la Loire"
              icon={MapPin}
            />
            <StatsCard
              title="Catégories"
              value={uniqueCategories}
              subtitle="Types d'événements"
              icon={Activity}
            />
            <StatsCard
              title="Dernière MAJ"
              value="10:30"
              subtitle="27 janvier 2026"
              icon={Database}
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

            {/* Main content - Events */}
            <div className="lg:col-span-2 space-y-6">
              <div>
                <h2 className="text-lg font-semibold mb-4">
                  Événements récents
                </h2>
                <FilterBar
                  searchQuery={searchQuery}
                  onSearchChange={setSearchQuery}
                  selectedCategory={selectedCategory}
                  onCategoryChange={setSelectedCategory}
                  selectedCity={selectedCity}
                  onCityChange={setSelectedCity}
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-4">
                  <p className="text-sm text-muted-foreground">
                    {filteredEvents.length} événement
                    {filteredEvents.length > 1 ? "s" : ""} trouvé
                    {filteredEvents.length > 1 ? "s" : ""}
                  </p>
                </div>
                <EventsTable
                  events={filteredEvents}
                  onSelectEvent={setSelectedEvent}
                />
              </div>
            </div>

            {/* Sidebar - Logs */}
            <div className="space-y-6">
              <LogsPanel logs={mockLogs} />

              {/* Quick info */}
              {/* <div className="rounded-xl border border-border bg-card p-6">
                <h3 className="font-semibold mb-4">Configuration</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Source</span>
                    <span className="font-medium">infolocale.fr</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Régions</span>
                    <span className="font-medium">Bretagne</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Fréquence</span>
                    <span className="font-medium">Quotidienne</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Géocodage</span>
                    <span className="font-medium text-success">Activé</span>
                  </div>
                </div>
              </div> */}
            </div>
          </div>
        </main>

        {/* Event Detail Sheet */}
        <EventDetailSheet
          event={selectedEvent}
          open={!!selectedEvent}
          onClose={() => setSelectedEvent(null)}
        />
      </div>
    </>
  )
}
