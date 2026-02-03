export type CategoryStyleVariant = "table" | "sheet"

const STYLES: Record<CategoryStyleVariant, Record<string, string>> = {
  table: {
    Concert: "bg-purple-100 text-purple-800 border-purple-200",
    Exposition: "bg-blue-100 text-blue-800 border-blue-200",
    Marché: "bg-green-100 text-green-800 border-green-200",
    Théâtre: "bg-red-100 text-red-800 border-red-200",
    Sport: "bg-orange-100 text-orange-800 border-orange-200",
    Festival: "bg-pink-100 text-pink-800 border-pink-200",
    Conférence: "bg-slate-100 text-slate-800 border-slate-200",
    Atelier: "bg-teal-100 text-teal-800 border-teal-200",
  },
  sheet: {
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
  },
}

export function getCategoryBadgeClass(
  category?: string | null,
  variant: CategoryStyleVariant = "sheet",
): string {
  return STYLES[variant][category ?? ""] ?? ""
}
