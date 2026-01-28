export interface ScannedEvent {
  id: number;
  uid: string;
  title: string;
  category: string;
  beginDate: string;
  endDate?: string;
  startTime?: string;
  endTime?: string;
  description: string;
  organizer: string;
  pricing?: string;
  website?: string;
  tags: string[];
  artists?: string[];
  locationName: string;
  address: string;
  zipcode: string;
  city: string;
  state: string;
  country: string;
  latitude?: number;
  longitude?: number;
  createdAt: string;
  isPrivate: boolean;
}

export const mockEvents: ScannedEvent[] = [
  {
    id: 1,
    uid: "evt-001-rennes-concert",
    title: "Concert Jazz au Liberté",
    category: "Concert",
    beginDate: "2026-02-15",
    startTime: "20:30",
    endTime: "23:00",
    description: "Une soirée jazz exceptionnelle avec le quartet de Thomas Music. Ambiance feutrée et sonorités envoûtantes au cœur de Rennes.",
    organizer: "Le Liberté - Scène nationale",
    pricing: "15€ - 25€",
    website: "https://www.leliberte.fr",
    tags: ["jazz", "musique", "live", "soirée"],
    artists: ["Thomas Music Quartet"],
    locationName: "Le Liberté",
    address: "1 Esplanade du Général de Gaulle",
    zipcode: "35000",
    city: "Rennes",
    state: "Ille-et-Vilaine",
    country: "France",
    latitude: 48.1113,
    longitude: -1.6800,
    createdAt: "2026-01-20T10:30:00Z",
    isPrivate: false,
  },
  {
    id: 2,
    uid: "evt-002-nantes-expo",
    title: "Exposition : L'Art Numérique",
    category: "Exposition",
    beginDate: "2026-02-01",
    endDate: "2026-03-15",
    startTime: "10:00",
    endTime: "18:00",
    description: "Plongez dans l'univers fascinant de l'art numérique avec plus de 50 œuvres interactives d'artistes internationaux.",
    organizer: "Musée d'Arts de Nantes",
    pricing: "Gratuit - 8€",
    tags: ["art", "numérique", "exposition", "interactif"],
    locationName: "Musée d'Arts de Nantes",
    address: "10 Rue Georges Clemenceau",
    zipcode: "44000",
    city: "Nantes",
    state: "Loire-Atlantique",
    country: "France",
    latitude: 47.2184,
    longitude: -1.5536,
    createdAt: "2026-01-18T14:00:00Z",
    isPrivate: false,
  },
  {
    id: 3,
    uid: "evt-003-brest-marche",
    title: "Marché de Producteurs Locaux",
    category: "Marché",
    beginDate: "2026-02-08",
    startTime: "08:00",
    endTime: "13:00",
    description: "Retrouvez les meilleurs producteurs locaux du Finistère pour un marché authentique en plein cœur de Brest.",
    organizer: "Association Terroirs Bretons",
    pricing: "Entrée libre",
    tags: ["marché", "local", "producteurs", "alimentation"],
    locationName: "Place de la Liberté",
    address: "Place de la Liberté",
    zipcode: "29200",
    city: "Brest",
    state: "Finistère",
    country: "France",
    latitude: 48.3904,
    longitude: -4.4861,
    createdAt: "2026-01-22T09:00:00Z",
    isPrivate: false,
  },
  {
    id: 4,
    uid: "evt-004-vannes-theatre",
    title: "Cyrano de Bergerac",
    category: "Théâtre",
    beginDate: "2026-02-20",
    startTime: "20:00",
    endTime: "22:30",
    description: "La célèbre pièce d'Edmond Rostand revisitée par la compagnie des Arts Vivants. Un Cyrano moderne et touchant.",
    organizer: "Théâtre Anne de Bretagne",
    pricing: "12€ - 28€",
    website: "https://www.theatre-vannes.fr",
    tags: ["théâtre", "classique", "comédie"],
    artists: ["Compagnie des Arts Vivants"],
    locationName: "Théâtre Anne de Bretagne",
    address: "Place de Bretagne",
    zipcode: "56000",
    city: "Vannes",
    state: "Morbihan",
    country: "France",
    latitude: 47.6559,
    longitude: -2.7603,
    createdAt: "2026-01-19T16:45:00Z",
    isPrivate: false,
  },
  {
    id: 5,
    uid: "evt-005-quimper-sport",
    title: "Trail des Montagnes Noires",
    category: "Sport",
    beginDate: "2026-03-01",
    startTime: "09:00",
    description: "Course nature de 25km à travers les paysages sauvages des Montagnes Noires. Ouvert à tous les niveaux.",
    organizer: "Running Club Quimper",
    pricing: "20€",
    website: "https://www.trail-montagnes-noires.bzh",
    tags: ["trail", "course", "nature", "sport"],
    locationName: "Parking du Stade",
    address: "Rue du Stade",
    zipcode: "29000",
    city: "Quimper",
    state: "Finistère",
    country: "France",
    latitude: 48.0000,
    longitude: -4.0997,
    createdAt: "2026-01-21T11:20:00Z",
    isPrivate: false,
  },
  {
    id: 6,
    uid: "evt-006-lorient-festival",
    title: "Festival Interceltique - Avant-première",
    category: "Festival",
    beginDate: "2026-02-28",
    startTime: "19:00",
    endTime: "23:00",
    description: "Soirée spéciale avant-première du Festival Interceltique avec concerts et dégustations.",
    organizer: "Festival Interceltique de Lorient",
    pricing: "25€",
    tags: ["festival", "celtique", "musique", "bretagne"],
    locationName: "Palais des Congrès",
    address: "Quai du Péristyle",
    zipcode: "56100",
    city: "Lorient",
    state: "Morbihan",
    country: "France",
    latitude: 47.7486,
    longitude: -3.3639,
    createdAt: "2026-01-23T08:00:00Z",
    isPrivate: false,
  },
  {
    id: 7,
    uid: "evt-007-saintmalo-conference",
    title: "Conférence : L'avenir du Maritime",
    category: "Conférence",
    beginDate: "2026-02-12",
    startTime: "14:00",
    endTime: "17:00",
    description: "Table ronde avec des experts du monde maritime sur les enjeux écologiques et économiques des océans.",
    organizer: "Chambre de Commerce Maritime",
    pricing: "Gratuit sur inscription",
    tags: ["conférence", "maritime", "écologie", "économie"],
    locationName: "Palais du Grand Large",
    address: "1 Quai Duguay-Trouin",
    zipcode: "35400",
    city: "Saint-Malo",
    state: "Ille-et-Vilaine",
    country: "France",
    latitude: 48.6493,
    longitude: -2.0007,
    createdAt: "2026-01-17T13:30:00Z",
    isPrivate: false,
  },
  {
    id: 8,
    uid: "evt-008-dinan-atelier",
    title: "Atelier Poterie pour Enfants",
    category: "Atelier",
    beginDate: "2026-02-22",
    startTime: "14:00",
    endTime: "16:00",
    description: "Initiation à la poterie pour les enfants de 6 à 12 ans. Chaque participant repart avec sa création.",
    organizer: "Maison des Arts",
    pricing: "8€",
    tags: ["atelier", "enfants", "poterie", "créatif"],
    locationName: "Maison des Arts",
    address: "5 Rue de l'Horloge",
    zipcode: "22100",
    city: "Dinan",
    state: "Côtes-d'Armor",
    country: "France",
    latitude: 48.4534,
    longitude: -2.0505,
    createdAt: "2026-01-24T10:00:00Z",
    isPrivate: false,
  },
];

export const categories = [
  "Concert",
  "Exposition",
  "Marché",
  "Théâtre",
  "Sport",
  "Festival",
  "Conférence",
  "Atelier",
];

export const cities = [
  "Rennes",
  "Nantes",
  "Brest",
  "Vannes",
  "Quimper",
  "Lorient",
  "Saint-Malo",
  "Dinan",
];

export interface ScrapingLog {
  id: number;
  timestamp: string;
  level: "INFO" | "WARNING" | "ERROR" | "DEBUG";
  message: string;
  details?: string;
}

export const mockLogs: ScrapingLog[] = [
  {
    id: 1,
    timestamp: "2026-01-27T10:30:00Z",
    level: "INFO",
    message: "Scraping démarré - Région Bretagne",
    details: "Cible: infolocale.fr/bretagne",
  },
  {
    id: 2,
    timestamp: "2026-01-27T10:30:05Z",
    level: "DEBUG",
    message: "Page 1/15 récupérée",
    details: "25 événements trouvés",
  },
  {
    id: 3,
    timestamp: "2026-01-27T10:30:12Z",
    level: "INFO",
    message: "Géocodage en cours",
    details: "API Google Places - 25 requêtes",
  },
  {
    id: 4,
    timestamp: "2026-01-27T10:30:18Z",
    level: "WARNING",
    message: "Événement sans adresse détectée",
    details: "UID: evt-temp-001 - Géocodage ignoré",
  },
  {
    id: 5,
    timestamp: "2026-01-27T10:30:25Z",
    level: "INFO",
    message: "Insertion base de données",
    details: "24 nouveaux / 1 doublon ignoré",
  },
  {
    id: 6,
    timestamp: "2026-01-27T10:30:30Z",
    level: "INFO",
    message: "Scraping terminé avec succès",
    details: "Durée: 30s - 24 événements ajoutés",
  },
];