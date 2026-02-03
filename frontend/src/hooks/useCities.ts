import { useEffect, useState } from "react"
import { fetchCities } from "@/api/infolocale"

export function useCities() {
  const [cities, setCities] = useState<string[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const controller = new AbortController()

    ;(async () => {
      try {
        setLoading(true)
        setCities(await fetchCities(controller.signal))
      } catch {
        setCities([])
      } finally {
        setLoading(false)
      }
    })()

    return () => controller.abort()
  }, [])

  return { cities, loading }
}
