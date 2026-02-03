export type Coords = { lat: number; lng: number }

export function getCoords(
  lat?: number | null,
  lng?: number | null,
): Coords | null {
  if (typeof lat !== "number" || !Number.isFinite(lat)) return null
  if (typeof lng !== "number" || !Number.isFinite(lng)) return null
  if (lat === 0 && lng === 0) return null
  return { lat, lng }
}
