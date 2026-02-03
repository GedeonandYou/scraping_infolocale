import { Calendar, ExternalLink, MapPin } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import type { ScannedEvent } from "@/data/Events"
import { formatShortDate } from "@/utils/date"
import { getCategoryBadgeClass } from "@/constants/categoryStyles"

interface EventsTableProps {
  events: ScannedEvent[]
  onSelectEvent: (event: ScannedEvent) => void
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
          {events.map((event) => {
            const tags = event.tags ?? []

            return (
              <TableRow
                key={event.id}
                className="event-row cursor-pointer"
                onClick={() => onSelectEvent(event)}
              >
                <TableCell>
                  <div className="space-y-1">
                    <p className="font-medium leading-tight">{event.title}</p>
                    <p className="text-sm text-muted-foreground truncate max-w-xs">
                      {event.organizer || "—"}
                    </p>
                  </div>
                </TableCell>

                <TableCell>
                  <Badge
                    variant="outline"
                    className={getCategoryBadgeClass(event.category, "table")}
                  >
                    {event.category || "—"}
                  </Badge>
                </TableCell>

                <TableCell>
                  <div className="flex items-center gap-1.5 text-sm">
                    <Calendar className="h-3.5 w-3.5 text-muted-foreground" />
                    {formatShortDate(event.beginDate)}
                    {event.startTime ? (
                      <span className="text-muted-foreground">
                        • {event.startTime}
                      </span>
                    ) : null}
                  </div>
                </TableCell>

                <TableCell>
                  <div className="flex items-center gap-1.5 text-sm">
                    <MapPin className="h-3.5 w-3.5 text-muted-foreground" />
                    <span>{event.city || "—"}</span>
                  </div>
                </TableCell>

                <TableCell>
                  <div className="flex items-center gap-1">
                    {tags.length === 0 ? (
                      <span className="text-xs text-muted-foreground">—</span>
                    ) : (
                      <>
                        {tags.slice(0, 2).map((tag) => (
                          <Badge
                            key={tag}
                            variant="secondary"
                            className="text-xs"
                          >
                            {tag}
                          </Badge>
                        ))}
                        {tags.length > 2 ? (
                          <span className="text-xs text-muted-foreground">
                            +{tags.length - 2}
                          </span>
                        ) : null}
                      </>
                    )}
                  </div>
                </TableCell>

                <TableCell className="text-right">
                  {event.website ? (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        window.open(event.website, "_blank", "noopener,noreferrer")
                      }}
                    >
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  ) : null}
                </TableCell>
              </TableRow>
            )
          })}
        </TableBody>
      </Table>
    </div>
  )
}
