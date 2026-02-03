import { useEffect, useState } from "react"
import { fetchEvents } from "@/api/infolocale"
import type { ScannedEvent } from "@/data/Events"

export function useEventsList() {
  const [events, setEvents] = useState<ScannedEvent[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()

    ;(async () => {
      try {
        setLoading(true)
        setError(null)
        const r = await fetchEvents(controller.signal)
        setEvents(r.events)
        setTotal(r.total)
      } catch (e) {
        if (e instanceof DOMException && e.name === "AbortError") return
        setError(e instanceof Error ? e.message : "Erreur inconnue")
      } finally {
        setLoading(false)
      }
    })()

    return () => controller.abort()
  }, [])

  return { events, total, loading, error }
}
