import { useEffect, useState } from "react"
import { fetchCategories } from "@/api/infolocale"

export function useCategories() {
  const [categories, setCategories] = useState<string[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const controller = new AbortController()

    ;(async () => {
      try {
        setLoading(true)
        setCategories(await fetchCategories(controller.signal))
      } catch {
        setCategories([])
      } finally {
        setLoading(false)
      }
    })()

    return () => controller.abort()
  }, [])

  return { categories, loading }
}
