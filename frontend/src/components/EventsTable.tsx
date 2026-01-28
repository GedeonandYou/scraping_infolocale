import { Calendar, MapPin,  ExternalLink } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { ScannedEvent } from "@/data/Events";

interface EventsTableProps {
  events: ScannedEvent[];
  onSelectEvent: (event: ScannedEvent) => void;
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
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export function EventsTable({ events, onSelectEvent }: EventsTableProps) {
  return (
    <div className="rounded-xl border border-border bg-card overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="bg-muted/50 hover:bg-muted/50">
            <TableHead className="font-semibold">Événement</TableHead>
            <TableHead className="font-semibold">Catégorie</TableHead>
            <TableHead className="font-semibold">Date</TableHead>
            <TableHead className="font-semibold">Lieu</TableHead>
            <TableHead className="font-semibold">Tags</TableHead>
            <TableHead className="text-right font-semibold">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {events.map((event) => (
            <TableRow
              key={event.id}
              className="event-row cursor-pointer"
              onClick={() => onSelectEvent(event)}
            >
              <TableCell>
                <div className="space-y-1">
                  <p className="font-medium leading-tight">{event.title}</p>
                  <p className="text-sm text-muted-foreground truncate max-w-xs">
                    {event.organizer}
                  </p>
                </div>
              </TableCell>
              <TableCell>
                <Badge
                  variant="outline"
                  className={categoryColors[event.category] || ""}
                >
                  {event.category}
                </Badge>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1.5 text-sm">
                  <Calendar className="h-3.5 w-3.5 text-muted-foreground" />
                  {formatDate(event.beginDate)}
                  {event.startTime && (
                    <span className="text-muted-foreground">
                      • {event.startTime}
                    </span>
                  )}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1.5 text-sm">
                  <MapPin className="h-3.5 w-3.5 text-muted-foreground" />
                  <span>{event.city}</span>
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1">
                  {event.tags.slice(0, 2).map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                  {event.tags.length > 2 && (
                    <span className="text-xs text-muted-foreground">
                      +{event.tags.length - 2}
                    </span>
                  )}
                </div>
              </TableCell>
              <TableCell className="text-right">
                {event.website && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      window.open(event.website, "_blank");
                    }}
                  >
                    <ExternalLink className="h-4 w-4" />
                  </Button>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}