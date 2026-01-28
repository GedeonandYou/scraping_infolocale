import type { ScannedEvent } from "@/data/Events";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  Calendar,
  Clock,
  MapPin,
  User,
  Euro,
  ExternalLink,
  Tag,
  Music,
} from "lucide-react";

interface EventDetailSheetProps {
  event: ScannedEvent | null;
  open: boolean;
  onClose: () => void;
}

const categoryColors: Record<string, string> = {
  Concert: "bg-purple-100 text-purple-800 border-purple-200",
  Exposition: "bg-blue-100 text-blue-800 border-blue-200",
  Marché: "bg-green-100 text-green-800 border-green-200",
  Théâtre: "bg-red-100 text-red-800 border-red-200",
  Sport: "bg-orange-100 text-orange-800 border-orange-200",
  Festival: "bg-pink-100 text-pink-800 border-pink-200",
  Conférence: "bg-slate-100 text-slate-800 border-slate-200",
  Atelier: "bg-teal-100 text-teal-800 border-teal-200",
};

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString("fr-FR", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

export function EventDetailSheet({ event, open, onClose }: EventDetailSheetProps) {
  if (!event) return null;

  return (
    <Sheet open={open} onOpenChange={onClose}>
      <SheetContent className="w-full sm:max-w-lg overflow-y-auto">
        <SheetHeader className="space-y-4">
          <div className="flex items-start justify-between">
            <Badge
              variant="outline"
              className={categoryColors[event.category] || ""}
            >
              {event.category}
            </Badge>
            <span className="text-xs text-muted-foreground font-mono">
              {event.uid}
            </span>
          </div>
          <SheetTitle className="text-xl leading-tight text-left">
            {event.title}
          </SheetTitle>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          {/* Date & Time */}
          <div className="space-y-3">
            <div className="flex items-center gap-3 text-sm">
              <Calendar className="h-4 w-4 text-primary" />
              <span className="font-medium">{formatDate(event.beginDate)}</span>
              {event.endDate && event.endDate !== event.beginDate && (
                <span className="text-muted-foreground">
                  → {formatDate(event.endDate)}
                </span>
              )}
            </div>
            {event.startTime && (
              <div className="flex items-center gap-3 text-sm">
                <Clock className="h-4 w-4 text-primary" />
                <span>
                  {event.startTime}
                  {event.endTime && ` - ${event.endTime}`}
                </span>
              </div>
            )}
          </div>

          <Separator />

          {/* Location */}
          <div className="space-y-2">
            <div className="flex items-start gap-3 text-sm">
              <MapPin className="h-4 w-4 text-primary mt-0.5" />
              <div>
                <p className="font-medium">{event.locationName}</p>
                <p className="text-muted-foreground">{event.address}</p>
                <p className="text-muted-foreground">
                  {event.zipcode} {event.city}, {event.state}
                </p>
              </div>
            </div>
            {event.latitude && event.longitude && (
              <p className="text-xs text-muted-foreground pl-7 font-mono">
                {event.latitude.toFixed(4)}, {event.longitude.toFixed(4)}
              </p>
            )}
          </div>

          <Separator />

          {/* Description */}
          <div>
            <h4 className="text-sm font-semibold mb-2">Description</h4>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {event.description}
            </p>
          </div>

          <Separator />

          {/* Details */}
          <div className="space-y-3">
            <div className="flex items-center gap-3 text-sm">
              <User className="h-4 w-4 text-primary" />
              <span>{event.organizer}</span>
            </div>
            {event.pricing && (
              <div className="flex items-center gap-3 text-sm">
                <Euro className="h-4 w-4 text-primary" />
                <span>{event.pricing}</span>
              </div>
            )}
            {event.artists && event.artists.length > 0 && (
              <div className="flex items-center gap-3 text-sm">
                <Music className="h-4 w-4 text-primary" />
                <span>{event.artists.join(", ")}</span>
              </div>
            )}
          </div>

          <Separator />

          {/* Tags */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Tag className="h-4 w-4 text-primary" />
              <h4 className="text-sm font-semibold">Tags</h4>
            </div>
            <div className="flex flex-wrap gap-2">
              {event.tags.map((tag) => (
                <Badge key={tag} variant="secondary">
                  {tag}
                </Badge>
              ))}
            </div>
          </div>

          {/* Actions */}
          {event.website && (
            <>
              <Separator />
              <Button
                className="w-full"
                onClick={() => window.open(event.website, "_blank")}
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Voir le site officiel
              </Button>
            </>
          )}

          {/* Metadata */}
          <div className="pt-4 text-xs text-muted-foreground">
            <p>
              Ajouté le{" "}
              {new Date(event.createdAt).toLocaleDateString("fr-FR", {
                day: "numeric",
                month: "long",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              })}
            </p>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
  }