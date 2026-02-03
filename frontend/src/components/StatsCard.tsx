import type { LucideIcon } from "lucide-react"

interface StatsCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: LucideIcon
  trend?: {
    value: number
    positive: boolean
  }
}

export function StatsCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
}: StatsCardProps) {
  return (
    <div className="relative overflow-hidden rounded-lg border border-border bg-card p-6 shadow-sm hover:shadow-md transition-shadow">
      <div className="absolute -right-8 -top-8 h-32 w-32 rounded-full bg-primary/5 blur-3xl" />

      <div className="relative flex items-start justify-between">
        <div className="space-y-2">
          <p className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
            {title}
          </p>
          <p className="text-4xl font-bold tracking-tight">{value}</p>

          {subtitle ? (
            <p className="text-xs text-muted-foreground pt-1">{subtitle}</p>
          ) : null}

          {trend ? (
            <p
              className={`text-xs font-semibold pt-2 ${
                trend.positive
                  ? "text-green-600 dark:text-green-400"
                  : "text-red-600 dark:text-red-400"
              }`}
            >
              <span className="inline-block mr-1">
                {trend.positive ? "↑" : "↓"}
              </span>
              {trend.positive ? "+" : ""}
              {trend.value}% vs semaine dernière
            </p>
          ) : null}
        </div>

        <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-linear-to-br from-blue-100 to-blue-50 dark:from-blue-950/40 dark:to-blue-900/20 ring-1 ring-blue-200 dark:ring-blue-800">
          <Icon className="h-6 w-6 text-blue-600 dark:text-blue-400" />
        </div>
      </div>
    </div>
  )
}
