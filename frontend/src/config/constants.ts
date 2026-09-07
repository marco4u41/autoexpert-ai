export const API_BASE_URL = "/api";

export const MESSAGE_ROLES = {
  USER: "user",
  ASSISTANT: "assistant",
  SYSTEM: "system",
} as const;

export const VEHICLE_BRANDS = [
  "Toyota",
  "Honda",
  "Ford",
  "Chevrolet",
  "Nissan",
  "Volkswagen",
  "Mazda",
  "Hyundai",
  "Kia",
  "Suzuki",
  "Mitsubishi",
  "BMW",
  "Mercedes-Benz",
  "Audi",
] as const;

export const DIAGNOSIS_CATEGORIES = [
  "Motor",
  "Transmisión",
  "Frenos",
  "Suspensión",
  "Eléctrico",
  "Refrigeración",
  "Escape",
  "Dirección",
  "Combustible",
  "General",
] as const;

export const TERRAIN_TYPES = [
  { value: "city", label: "Urbano" },
  { value: "highway", label: "Autopista" },
  { value: "offroad", label: "Todo terreno" },
  { value: "mixed", label: "Mixto" },
] as const;

export const ENGINE_TYPES = [
  { value: "gasoline", label: "Gasolina" },
  { value: "diesel", label: "Diésel" },
  { value: "electric", label: "Eléctrico" },
  { value: "hybrid", label: "Híbrido" },
] as const;

export const GARAGE_MAX_ITEMS = 10;

export const MAX_MESSAGE_LENGTH = 2000;
export const TYPING_INDICATOR_DELAY = 300;

export const GARAGE_STORAGE_KEY = "autoexpert-garage";
