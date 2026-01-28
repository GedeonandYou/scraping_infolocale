import { ScrollArea } from "@/components/ui/scroll-area"
import type { ScrapingLog } from "@/data/Events"
import { AlertCircle, AlertTriangle, Bug, Info } from "lucide-react"

interface LogsPanelProps {
  logs: ScrapingLog[]
}

const levelConfig = {
  INFO: {
    icon: Info,
    className:
      "text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/30 ring-1 ring-blue-200 dark:ring-blue-800",
  },
  WARNING: {
    icon: AlertTriangle,
    className:
      "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/30 ring-1 ring-amber-200 dark:ring-amber-800",
  },
  ERROR: {
    icon: AlertCircle,
    className:
      "text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/30 ring-1 ring-red-200 dark:ring-red-800",
  },
  DEBUG: {
    icon: Bug,
    className:
      "text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-950/30 ring-1 ring-slate-200 dark:ring-slate-800",
  },
}

function formatTimestamp(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString("fr-FR", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  })
}

export function LogsPanel({ logs }: LogsPanelProps) {
  return (
    <div className="rounded-lg border border-border bg-card overflow-hidden shadow-sm">
      <div className="p-5 border-b border-border bg-linear-to-r from-muted/50 to-transparent">
        <h3 className="font-semibold text-base">Logs de Scraping</h3>
        <p className="text-xs text-muted-foreground mt-1">
          Dernière exécution : 27 janvier 2026
        </p>
      </div>
      <ScrollArea className="h-80">
        <div className="p-4 space-y-2">
          {logs.map((log) => {
            const config = levelConfig[log.level]
            const Icon = config.icon
            return (
              <div
                key={log.id}
                className="flex items-start gap-3 p-3 rounded-md bg-muted/40 hover:bg-muted/60 transition-colors border border-transparent hover:border-border/50"
              >
                <div
                  className={`p-2 rounded-md shrink-0 ${config.className}`}
                >
                  <Icon className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-mono text-muted-foreground bg-muted/50 px-2 py-1 rounded">
                      {formatTimestamp(log.timestamp)}
                    </span>
                    <span className="text-xs font-semibold uppercase tracking-wide px-2 py-1 rounded-sm bg-muted/30">
                      {log.level}
                    </span>
                  </div>
                  <p className="text-sm font-medium mt-2 text-foreground">
                    {log.message}
                  </p>
                  {log.details && (
                    <p className="text-xs text-muted-foreground mt-1.5 opacity-75">
                      {log.details}
                    </p>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </ScrollArea>
    </div>
  )
}
