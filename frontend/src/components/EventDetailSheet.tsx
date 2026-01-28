import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import {
  Sheet,
  SheetContent,
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

interface EventDetailSheetProps {
  event: ScannedEvent | null
  open: boolean
  onClose: () => void
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

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString("fr-FR", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  })
}

export function EventDetailSheet({
  event,
  open,
  onClose,
}: EventDetailSheetProps) {
  if (!event) return null

  return (
    <Sheet open={open} onOpenChange={onClose}>
      <SheetContent className="w-full sm:max-w-lg overflow-y-auto bg-linear-to-b from-card via-card to-muted/5 p-5">
        <SheetHeader className="space-y-4 pb-6 border-b border-border">
          <div className="flex items-start justify-between gap-3">
            <Badge
              variant="outline"
              className={categoryColors[event.category] || ""}
            >
              {event.category}
            </Badge>
            <span className="text-xs text-muted-foreground font-mono bg-muted/50 px-2 py-1 rounded">
              ID: {event.uid}
            </span>
          </div>
          <SheetTitle className="text-2xl leading-tight text-left font-bold">
            {event.title}
          </SheetTitle>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          {/* Date & Time */}
          <div className="space-y-3 bg-muted/30 p-4 rounded-lg border border-border/50">
            <div className="flex items-center gap-3 text-sm">
              <div className="p-2 rounded bg-primary/10">
                <Calendar className="h-4 w-4 text-primary" />
              </div>
              <div>
                <p className="font-semibold">{formatDate(event.beginDate)}</p>
                {event.endDate && event.endDate !== event.beginDate && (
                  <p className="text-xs text-muted-foreground">
                    jusqu'au {formatDate(event.endDate)}
                  </p>
                )}
              </div>
            </div>
            {event.startTime && (
              <div className="flex items-center gap-3 text-sm mt-2">
                <div className="p-2 rounded bg-primary/10">
                  <Clock className="h-4 w-4 text-primary" />
                </div>
                <span className="font-medium">
                  {event.startTime}
                  {event.endTime && ` - ${event.endTime}`}
                </span>
              </div>
            )}
          </div>

          <Separator />

          {/* Location */}
          <div className="space-y-3 bg-muted/30 p-4 rounded-lg border border-border/50">
            <div className="flex items-start gap-3 text-sm">
              <div className="p-2 rounded bg-primary/10 flex-shrink-0">
                <MapPin className="h-4 w-4 text-primary" />
              </div>
              <div className="flex-1">
                <p className="font-semibold">{event.locationName}</p>
                <p className="text-sm text-muted-foreground mt-1">
                  {event.address}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {event.zipcode} {event.city}, {event.state}
                </p>
                {event.latitude && event.longitude && (
                  <p className="text-xs text-muted-foreground mt-2 font-mono bg-muted/40 p-1.5 rounded inline-block">
                    📍 {event.latitude.toFixed(4)}, {event.longitude.toFixed(4)}
                  </p>
                )}
              </div>
            </div>
          </div>

          <Separator />

          {/* Description */}
          <div className="bg-muted/20 p-4 rounded-lg border border-border/50">
            <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
              <span className="inline-block w-1 h-4 bg-primary rounded-full"></span>
              Description
            </h4>
            <p className="text-sm leading-relaxed text-foreground">
              {event.description}
            </p>
          </div>

          <Separator />

          {/* Details */}
          <div className="space-y-3 bg-muted/30 p-4 rounded-lg border border-border/50">
            <div className="flex items-center gap-3 text-sm">
              <div className="p-2 rounded bg-primary/10">
                <User className="h-4 w-4 text-primary" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Organisateur</p>
                <p className="font-medium">{event.organizer}</p>
              </div>
            </div>
            {event.pricing && (
              <div className="flex items-center gap-3 text-sm">
                <div className="p-2 rounded bg-primary/10">
                  <Euro className="h-4 w-4 text-primary" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Tarif</p>
                  <p className="font-medium">{event.pricing}</p>
                </div>
              </div>
            )}
            {event.artists && event.artists.length > 0 && (
              <div className="flex items-start gap-3 text-sm">
                <div className="p-2 rounded bg-primary/10 shrink-0">
                  <Music className="h-4 w-4 text-primary" />
                </div>
                <div className="flex-1">
                  <p className="text-xs text-muted-foreground">Artistes</p>
                  <p className="font-medium">{event.artists.join(", ")}</p>
                </div>
              </div>
            )}
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
              {event.tags.map((tag) => (
                <Badge
                  key={tag}
                  variant="secondary"
                  className="bg-primary/10 text-primary hover:bg-primary/20 border-primary/20"
                >
                  #{tag}
                </Badge>
              ))}
            </div>
          </div>

          {/* Actions */}
          {event.website && (
            <Button
              className="w-full bg-linear-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 text-primary-foreground font-semibold h-10 rounded-lg transition-all"
              onClick={() => window.open(event.website, "_blank")}
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              Voir le site officiel
            </Button>
          )}
          
        </div>
      </SheetContent>
    </Sheet>
  )
}
