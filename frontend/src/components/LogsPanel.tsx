import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { AlertCircle, CheckCircle2, Info, Terminal } from "lucide-react"

type LogLevel = "info" | "success" | "warning" | "error" | string

export interface LogItem {
  time: string
  message: string
  level?: LogLevel
}

interface LogsPanelProps {
  logs: LogItem[]
}

const levelConfig: Record<string, { icon: any; label: string; badgeClass: string }> = {
  info: {
    icon: Info,
    label: "Info",
    badgeClass: "bg-blue-100 text-blue-800 border-blue-200",
  },
  success: {
    icon: CheckCircle2,
    label: "Succès",
    badgeClass: "bg-green-100 text-green-800 border-green-200",
  },
  warning: {
    icon: AlertCircle,
    label: "Alerte",
    badgeClass: "bg-yellow-100 text-yellow-800 border-yellow-200",
  },
  error: {
    icon: AlertCircle,
    label: "Erreur",
    badgeClass: "bg-red-100 text-red-800 border-red-200",
  },
}

const fallbackLevel = levelConfig.info

export function LogsPanel({ logs }: LogsPanelProps) {
  return (
    <Card className="rounded-xl border-border">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <Terminal className="h-4 w-4" />
          Logs
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-3">
        {(!logs || logs.length === 0) && (
          <p className="text-sm text-muted-foreground">Aucun log pour le moment.</p>
        )}

        {logs?.map((log, idx) => {
          // ✅ fallback si level manquant ou inconnu
          const cfg = levelConfig[String(log.level ?? "info")] ?? fallbackLevel
          const Icon = cfg.icon

          return (
            <div
              key={`${log.time}-${idx}`}
              className="flex items-start justify-between gap-3 rounded-lg border border-border/60 bg-muted/20 p-3"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <Icon className="h-4 w-4 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground">{log.time}</span>
                </div>
                <p className="text-sm mt-1 wrap-break-word">{log.message}</p>
              </div>

              <Badge variant="outline" className={cfg.badgeClass}>
                {cfg.label}
              </Badge>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}
