import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { categories, cities } from "@/data/Events"
import { Filter, Search, X } from "lucide-react"

interface FilterBarProps {
  searchQuery: string
  onSearchChange: (query: string) => void
  selectedCategory: string | null
  onCategoryChange: (category: string | null) => void
  selectedCity: string | null
  onCityChange: (city: string | null) => void
}

export function FilterBar({
  searchQuery,
  onSearchChange,
  selectedCategory,
  onCategoryChange,
  selectedCity,
  onCityChange,
}: FilterBarProps) {
  const hasFilters = searchQuery || selectedCategory || selectedCity

  const clearFilters = () => {
    onSearchChange("")
    onCategoryChange(null)
    onCityChange(null)
  }

  return (
    <div className="space-y-4">
      <div className="rounded-lg  from-card to-muted/5 ">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Rechercher un événement..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="pl-11 border-border/50 bg-background/50 hover:bg-background/70 focus:bg-background transition-colors"
            />
          </div>
          <Select
            value={selectedCategory || "all"}
            onValueChange={(value) =>
              onCategoryChange(value === "all" ? null : value)
            }
          >
            <SelectTrigger className="w-full sm:w-48 border-border/50 bg-background/50 hover:bg-background/70 focus:bg-background">
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4" />
                <SelectValue placeholder="Catégorie" />
              </div>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Toutes catégories</SelectItem>
              {categories.map((category) => (
                <SelectItem key={category} value={category}>
                  {category}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select
            value={selectedCity || "all"}
            onValueChange={(value) =>
              onCityChange(value === "all" ? null : value)
            }
          >
            <SelectTrigger className="w-full sm:w-48 border-border/50 bg-background/50 hover:bg-background/70 focus:bg-background">
              <div className="flex items-center gap-2">
                <span>📍</span>
                <SelectValue placeholder="Ville" />
              </div>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Toutes les villes</SelectItem>
              {cities.map((city) => (
                <SelectItem key={city} value={city}>
                  {city}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {hasFilters && (
        <div className="flex flex-wrap items-center gap-2 bg-muted/30 p-3 rounded-lg ">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-foreground">
              Filtres actifs :
            </span>
          </div>
          {searchQuery && (
            <Badge className="gap-1 bg-primary/10 text-primary hover:bg-primary/20 border border-primary/20">
              🔍 "{searchQuery}"
              <X
                className="h-3 w-3 cursor-pointer hover:opacity-70"
                onClick={() => onSearchChange("")}
              />
            </Badge>
          )}
          {selectedCategory && (
            <Badge className="gap-1 bg-primary/10 text-primary hover:bg-primary/20 border border-primary/20">
              📂 {selectedCategory}
              <X
                className="h-3 w-3 cursor-pointer hover:opacity-70"
                onClick={() => onCategoryChange(null)}
              />
            </Badge>
          )}
          {selectedCity && (
            <Badge className="gap-1 bg-primary/10 text-primary hover:bg-primary/20 border border-primary/20">
              📍 {selectedCity}
              <X
                className="h-3 w-3 cursor-pointer hover:opacity-70"
                onClick={() => onCityChange(null)}
              />
            </Badge>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={clearFilters}
            className="ml-auto hover:bg-destructive/10 hover:text-destructive"
          >
            ✕ Effacer tout
          </Button>
        </div>
      )}
    </div>
  )
}
