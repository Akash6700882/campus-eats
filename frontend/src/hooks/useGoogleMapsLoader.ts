import { useJsApiLoader } from "@react-google-maps/api";

const LIBRARIES: "drawing"[] = ["drawing"];

/** Shared loader for the Google Maps JS API — reuse this hook everywhere a
 * map is rendered so the script/libraries are only ever loaded once. */
export function useGoogleMapsLoader() {
  return useJsApiLoader({
    id: "campus-eats-google-maps",
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
    libraries: LIBRARIES,
  });
}
