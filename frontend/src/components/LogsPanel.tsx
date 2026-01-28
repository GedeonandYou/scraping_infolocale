import type { ScrapingLog } from "@/data/Events";
import { ScrollArea } from "@/components/ui/scroll-area";
import { AlertCircle, AlertTriangle, Info, Bug } from "lucide-react";

interface LogsPanelProps {
  logs: ScrapingLog[];
}

const levelConfig = {
  INFO: {
    icon: Info,
    className: "text-primary bg-primary/10",
  },
  WARNING: {
    icon: AlertTriangle,
    className: "text-warning bg-warning/10",
  },
  ERROR: {
    icon: AlertCircle,
    className: "text-destructive bg-destructive/10",
  },
  DEBUG: {
    icon: Bug,
    className: "text-muted-foreground bg-muted",
  },
};

function formatTimestamp(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString("fr-FR", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function LogsPanel({ logs }: LogsPanelProps) {
  return (
    <div className="rounded-xl border border-border bg-card overflow-hidden">
      <div className="p-4 border-b border-border bg-muted/30">
        <h3 className="font-semibold">Logs de Scraping</h3>
        <p className="text-sm text-muted-foreground">
          Dernière exécution : 27 janvier 2026
        </p>
      </div>
      <ScrollArea className="h-80">
        <div className="p-4 space-y-2">
          {logs.map((log) => {
            const config = levelConfig[log.level];
            const Icon = config.icon;
            return (
              <div
                key={log.id}
                className="flex items-start gap-3 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors"
              >
                <div className={`p-1.5 rounded ${config.className}`}>
                  <Icon className="h-3.5 w-3.5" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-muted-foreground">
                      {formatTimestamp(log.timestamp)}
                    </span>
                    <span className="text-xs font-semibold uppercase text-muted-foreground">
                      {log.level}
                    </span>
                  </div>
                  <p className="text-sm font-medium mt-1">{log.message}</p>
                  {log.details && (
                    <p className="text-xs text-muted-foreground mt-1">
                      {log.details}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </ScrollArea>
    </div>
  );
}