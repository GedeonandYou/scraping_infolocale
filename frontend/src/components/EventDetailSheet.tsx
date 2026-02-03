// src/components/EventDetailSheet.tsx

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import type { ScannedEvent } from "@/data/Events"
import {
  Calendar,
  Clock,
  Euro,
  ExternalLink,
  MapPin,
  Music,
  Tag,
  User,
} from "lucide-react"

import L from "leaflet"
import "leaflet/dist/leaflet.css"
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet"

import iconRetinaUrl from "leaflet/dist/images/marker-icon-2x.png"
import iconUrl from "leaflet/dist/images/marker-icon.png"
import shadowUrl from "leaflet/dist/images/marker-shadow.png"

/** ✅ Fix Leaflet marker icons (Vite/React) */
declare global {
  interface Window {
    __leafletIconFixApplied?: boolean
  }
}
if (typeof window !== "undefined" && !window.__leafletIconFixApplied) {
  const proto = L.Icon.Default.prototype as unknown as Record<string, unknown>
  // Leaflet cherche une URL via une méthode interne. Sous Vite, on la supprime puis on remap.
  delete proto._getIconUrl
  L.Icon.Default.mergeOptions({ iconRetinaUrl, iconUrl, shadowUrl })
  window.__leafletIconFixApplied = true
}

interface EventDetailSheetProps {
  event: ScannedEvent | null
  open: boolean
  onClose: () => void
  loading?: boolean
  error?: string | null
}

const categoryColors: Record<string, string> = {
  Concert:
    "bg-gradient-to-r from-purple-100 to-purple-50 dark:from-purple-950/50 dark:to-purple-900/30 text-purple-800 dark:text-purple-300 border border-purple-200 dark:border-purple-800",
  Exposition:
    "bg-gradient-to-r from-blue-100 to-blue-50 dark:from-blue-950/50 dark:to-blue-900/30 text-blue-800 dark:text-blue-300 border border-blue-200 dark:border-blue-800",
  Marché:
    "bg-gradient-to-r from-green-100 to-green-50 dark:from-green-950/50 dark:to-green-900/30 text-green-800 dark:text-green-300 border border-green-200 dark:border-green-800",
  Théâtre:
    "bg-gradient-to-r from-red-100 to-red-50 dark:from-red-950/50 dark:to-red-900/30 text-red-800 dark:text-red-300 border border-red-200 dark:border-red-800",
  Sport:
    "bg-gradient-to-r from-orange-100 to-orange-50 dark:from-orange-950/50 dark:to-orange-900/30 text-orange-800 dark:text-orange-300 border border-orange-200 dark:border-orange-800",
  Festival:
    "bg-gradient-to-r from-pink-100 to-pink-50 dark:from-pink-950/50 dark:to-pink-900/30 text-pink-800 dark:text-pink-300 border border-pink-200 dark:border-pink-800",
  Conférence:
    "bg-gradient-to-r from-slate-100 to-slate-50 dark:from-slate-950/50 dark:to-slate-900/30 text-slate-800 dark:text-slate-300 border border-slate-200 dark:border-slate-800",
  Atelier:
    "bg-gradient-to-r from-teal-100 to-teal-50 dark:from-teal-950/50 dark:to-teal-900/30 text-teal-800 dark:text-teal-300 border border-teal-200 dark:border-teal-800",
}

function formatDate(dateString?: string | null): string {
  if (!dateString) return "—"
  const d = new Date(dateString)
  if (Number.isNaN(d.getTime())) return "—"
  return d.toLocaleDateString("fr-FR", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  })
}

function cleanText(s?: string | null): string {
  if (!s) return ""
  return String(s).replace(/\s+/g, " ").trim()
}

function getCoords(
  lat?: number | null,
  lng?: number | null,
): { lat: number; lng: number } | null {
  if (typeof lat !== "number" || !Number.isFinite(lat)) return null
  if (typeof lng !== "number" || !Number.isFinite(lng)) return null
  if (lat === 0 && lng === 0) return null
  return { lat, lng }
}

function getTileConfig(): { url: string; attribution: string; label: string } {
  const orsKey = import.meta.env.VITE_ORS_API_KEY as string | undefined

  if (orsKey && orsKey.trim().length > 0) {
    return {
      url: `https://api.openrouteservice.org/pmapsurfer/{z}/{x}/{y}.png?api_key=${encodeURIComponent(
        orsKey,
      )}`,
      attribution:
        "&copy; openrouteservice / HeiGIT &copy; OpenStreetMap contributors",
      label: "ORS MapSurfer",
    }
  }

  return {
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution: "&copy; OpenStreetMap contributors",
    label: "OpenStreetMap (fallback)",
  }
}

function openNewTab(url: string) {
  window.open(url, "_blank", "noopener,noreferrer")
}

export function EventDetailSheet({
  event,
  open,
  onClose,
  loading = false,
  error = null,
}: EventDetailSheetProps) {
  const tags = (event?.tags ?? []).filter((t) => t.trim().length > 0)
  const artists = (event?.artists ?? []).filter((a) => a.trim().length > 0)

  const description = cleanText(event?.description)
  const hasDescription = description.length > 0

  const coords = getCoords(event?.latitude ?? null, event?.longitude ?? null)
  const tile = getTileConfig()

  const openInORS = () => {
    if (!coords) return
    const url = `https://maps.openrouteservice.org/directions?n1=${coords.lat}&n2=${coords.lng}&n3=16&b=0&c=0&k1=fr-FR&k2=km`
    openNewTab(url)
  }

  const openInOSM = () => {
    if (!coords) return
    const url = `https://www.openstreetmap.org/?mlat=${coords.lat}&mlon=${coords.lng}#map=16/${coords.lat}/${coords.lng}`
    openNewTab(url)
  }

  return (
    <Sheet
      open={open}
      onOpenChange={(isOpen) => {
        if (!isOpen) onClose()
      }}
    >
      <SheetContent className="w-full sm:max-w-lg overflow-y-auto bg-gradient-to-b from-card via-card to-muted/5 p-5">
        <SheetHeader className="space-y-2 pb-6 border-b border-border">
          <div className="flex items-start justify-between gap-3">
            <Badge
              variant="outline"
              className={categoryColors[event?.category ?? ""] || ""}
            >
              {event?.category || "—"}
            </Badge>
          </div>

          <SheetTitle className="text-2xl leading-tight text-left font-bold">
            {event?.title || (loading ? "Chargement..." : "—")}
          </SheetTitle>

          <SheetDescription className="text-sm text-muted-foreground">
            {event
              ? `${event.city || "—"} • ${formatDate(event.beginDate)}`
              : "Détails de l’événement"}
          </SheetDescription>

          {error ? <p className="text-sm text-red-600">❌ {error}</p> : null}
          {loading ? (
            <p className="text-sm text-muted-foreground">
              ⏳ Chargement des détails...
            </p>
          ) : null}
        </SheetHeader>

        <div className="mt-6 space-y-6">
          {!event && !loading ? (
            <p className="text-sm text-muted-foreground">
              Aucun détail à afficher.
            </p>
          ) : null}

          {event ? (
            <>
              {/* Date & Time */}
              <div className="space-y-3 bg-muted/30 p-4 rounded-lg border border-border/50">
                <div className="flex items-center gap-3 text-sm">
                  <div className="p-2 rounded bg-primary/10">
                    <Calendar className="h-4 w-4 text-primary" />
                  </div>
                  <div>
                    <p className="font-semibold">{formatDate(event.beginDate)}</p>
                    {event.endDate && event.endDate !== event.beginDate ? (
                      <p className="text-xs text-muted-foreground">
                        jusqu&apos;au {formatDate(event.endDate)}
                      </p>
                    ) : null}
                  </div>
                </div>

                {event.startTime ? (
                  <div className="flex items-center gap-3 text-sm mt-2">
                    <div className="p-2 rounded bg-primary/10">
                      <Clock className="h-4 w-4 text-primary" />
                    </div>
                    <span className="font-medium">
                      {event.startTime}
                      {event.endTime ? ` - ${event.endTime}` : ""}
                    </span>
                  </div>
                ) : null}
              </div>

              <Separator />

              {/* Location + Map */}
              <div className="space-y-3 bg-muted/30 p-4 rounded-lg border border-border/50">
                <div className="flex items-start gap-3 text-sm">
                  <div className="p-2 rounded bg-primary/10 shrink-0">
                    <MapPin className="h-4 w-4 text-primary" />
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold">{event.locationName || "—"}</p>

                    {event.address ? (
                      <p className="text-sm text-muted-foreground mt-1">
                        {event.address}
                      </p>
                    ) : null}

                    <p className="text-xs text-muted-foreground mt-1">
                      {[event.zipcode, event.city, event.state]
                        .filter(Boolean)
                        .join(" ")}
                    </p>

                    {coords ? (
                      <p className="text-xs text-muted-foreground mt-2 font-mono bg-muted/40 p-1.5 rounded inline-block">
                        📍 {coords.lat.toFixed(5)}, {coords.lng.toFixed(5)}
                      </p>
                    ) : (
                      <p className="text-xs text-muted-foreground mt-2">
                        📍 Coordonnées indisponibles
                      </p>
                    )}
                  </div>
                </div>

                {coords ? (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <p className="text-xs text-muted-foreground">
                        Carte:{" "}
                        <span className="font-medium text-foreground">
                          {tile.label}
                        </span>
                      </p>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm" onClick={openInOSM}>
                          OSM
                        </Button>
                        <Button variant="outline" size="sm" onClick={openInORS}>
                          ORS
                        </Button>
                      </div>
                    </div>

                    <div className="h-56 w-full overflow-hidden rounded-lg border border-border/60">
                      <MapContainer
                        key={`${coords.lat}-${coords.lng}`}
                        center={[coords.lat, coords.lng]}
                        zoom={15}
                        scrollWheelZoom={false}
                        style={{ height: "100%", width: "100%" }}
                      >
                        <TileLayer url={tile.url} attribution={tile.attribution} />

                        <Marker position={[coords.lat, coords.lng]}>
                          <Popup>
                            <div className="text-xs">
                              <div className="font-semibold">
                                {event.title || "Événement"}
                              </div>
                              <div className="text-muted-foreground">
                                {event.locationName || ""}
                              </div>
                            </div>
                          </Popup>
                        </Marker>
                      </MapContainer>
                    </div>
                  </div>
                ) : null}
              </div>

              <Separator />

              {/* Description */}
              <div className="bg-muted/20 p-4 rounded-lg border border-border/50">
                <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <span className="inline-block w-1 h-4 bg-primary rounded-full" />
                  Description
                </h4>

                {hasDescription ? (
                  <p className="text-sm leading-relaxed text-foreground whitespace-pre-wrap">
                    {description}
                  </p>
                ) : (
                  <p className="text-sm text-muted-foreground">
                    Aucune description disponible.
                  </p>
                )}
              </div>

              <Separator />

              {/* Details */}
              <div className="space-y-3 bg-muted/30 p-4 rounded-lg border border-border/50">
                {/* Organisateur */}
                <div className="flex items-center gap-3 text-sm">
                  <div className="p-2 rounded bg-primary/10">
                    <User className="h-4 w-4 text-primary" />
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Organisateur</p>
                    <p className="font-medium">
                      {event.organizer?.trim() ? event.organizer : "—"}
                    </p>
                  </div>
                </div>

                {/* Tarif */}
                <div className="flex items-center gap-3 text-sm">
                  <div className="p-2 rounded bg-primary/10">
                    <Euro className="h-4 w-4 text-primary" />
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Tarif</p>
                    <p className="font-medium">
                      {event.pricing?.trim() ? event.pricing : "—"}
                    </p>
                  </div>
                </div>

                {/* Website */}
                <div className="flex items-center justify-between gap-3 text-sm">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="p-2 rounded bg-primary/10">
                      <ExternalLink className="h-4 w-4 text-primary" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-xs text-muted-foreground">Site officiel</p>
                      <p className="font-medium truncate max-w-60">
                        {event.website?.trim() ? event.website : "—"}
                      </p>
                    </div>
                  </div>

                  {event.website?.trim() ? (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => openNewTab(event.website!)}
                    >
                      Ouvrir
                    </Button>
                  ) : null}
                </div>

                {/* Artistes */}
                {artists.length > 0 ? (
                  <div className="flex items-start gap-3 text-sm">
                    <div className="p-2 rounded bg-primary/10 shrink-0">
                      <Music className="h-4 w-4 text-primary" />
                    </div>
                    <div className="flex-1">
                      <p className="text-xs text-muted-foreground">Artistes</p>
                      <p className="font-medium">{artists.join(", ")}</p>
                    </div>
                  </div>
                ) : null}
              </div>

              <Separator />

              {/* Tags */}
              <div className="bg-muted/20 p-4 rounded-lg border border-border/50">
                <div className="flex items-center gap-2 mb-3">
                  <div className="p-1.5 rounded bg-primary/10">
                    <Tag className="h-4 w-4 text-primary" />
                  </div>
                  <h4 className="text-sm font-semibold">Tags</h4>
                </div>

                <div className="flex flex-wrap gap-2">
                  {tags.length === 0 ? (
                    <span className="text-xs text-muted-foreground">
                      Aucun tag.
                    </span>
                  ) : (
                    tags.map((tag) => (
                      <Badge
                        key={tag}
                        variant="secondary"
                        className="bg-primary/10 text-primary hover:bg-primary/20 border-primary/20"
                      >
                        #{tag}
                      </Badge>
                    ))
                  )}
                </div>
              </div>

              {/* CTA */}
              {event.website?.trim() ? (
                <Button
                  className="w-full font-semibold h-10 rounded-lg"
                  onClick={() => openNewTab(event.website!)}
                >
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Voir le site officiel
                </Button>
              ) : null}
            </>
          ) : null}
        </div>
      </SheetContent>
    </Sheet>
  )
}
