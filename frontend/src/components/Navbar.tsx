import { Button } from "@/components/ui/button"
import { Menu, X } from "lucide-react"
import { useState } from "react"

export default function Navbar() {
  /**
   * ! STATE (état, données) de l'application
   */
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  /**
   * ! COMPORTEMENT (méthodes, fonctions) de l'application
   */
  const toggleMenu = () => setIsMenuOpen(!isMenuOpen)

  /**
   * ! AFFICHAGE (render) de l'application
   */
  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <a href="/" className="text-2xl font-bold text-blue-600">
              InfoLocale
            </a>
          </div>

          {/* Menu Desktop */}
          <div className="hidden md:flex items-center space-x-8">
            <a
              href="/"
              className="text-gray-700 hover:text-blue-600 transition"
            >
              Accueil
            </a>
            <a
              href="/events"
              className="text-gray-700 hover:text-blue-600 transition"
            >
              Événements
            </a>
            <a
              href="/cities"
              className="text-gray-700 hover:text-blue-600 transition"
            >
              Villes
            </a>
            <a
              href="/about"
              className="text-gray-700 hover:text-blue-600 transition"
            >
              À propos
            </a>
          </div>

          {/* Buttons Desktop */}
          <div className="hidden md:flex items-center space-x-4">
            <Button variant="outline">Connexion</Button>
            <Button>Inscription</Button>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={toggleMenu}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:bg-gray-100 transition"
            >
              {isMenuOpen ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden pb-4">
            <a
              href="/"
              className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100"
            >
              Accueil
            </a>
            <a
              href="/events"
              className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100"
            >
              Événements
            </a>
            <a
              href="/cities"
              className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100"
            >
              Villes
            </a>
            <a
              href="/about"
              className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100"
            >
              À propos
            </a>
            <div className="mt-4 space-y-2">
              <Button variant="outline" className="w-full">
                Connexion
              </Button>
              <Button className="w-full">Inscription</Button>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
