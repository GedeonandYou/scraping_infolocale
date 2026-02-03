import { useCallback, useEffect, useRef, useState } from "react"
import { fetchEventDetail } from "@/api/infolocale"
import type { ScannedEvent } from "@/data/Events"

export function useEventDetail() {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [event, setEvent] = useState<ScannedEvent | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const cacheRef = useRef<Map<string, ScannedEvent>>(new Map())

  const open = useCallback((preview: ScannedEvent) => {
    setEvent(preview)
    setSelectedId(String(preview.id))
  }, [])

  const close = useCallback(() => {
    setSelectedId(null)
    setEvent(null)
    setError(null)
    setLoading(false)
  }, [])

  useEffect(() => {
    if (!selectedId) return
    const controller = new AbortController()

    ;(async () => {
      try {
        setLoading(true)
        setError(null)

        const cached = cacheRef.current.get(selectedId)
        if (cached) {
          setEvent(cached)
          return
        }

        const full = await fetchEventDetail(selectedId, controller.signal)
        cacheRef.current.set(selectedId, full)
        setEvent(full)
      } catch (e) {
        if (e instanceof DOMException && e.name === "AbortError") return
        setError(e instanceof Error ? e.message : "Erreur inconnue")
      } finally {
        setLoading(false)
      }
    })()

    return () => controller.abort()
  }, [selectedId])

  return { isOpen: !!selectedId, event, loading, error, open, close }
}
