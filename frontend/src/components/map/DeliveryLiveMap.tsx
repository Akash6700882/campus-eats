import { GoogleMap, Marker } from "@react-google-maps/api";
import { useGoogleMapsLoader } from "@/hooks/useGoogleMapsLoader";
import { MapStatusNotice } from "@/components/map/MapStatusNotice";
import { CAMPUS_MAP_DEFAULT_ZOOM } from "@/lib/campus";

const MAP_CONTAINER_STYLE = { width: "100%", height: "200px", borderRadius: "0.75rem" };

export function DeliveryLiveMap({ latitude, longitude }: { latitude: number | null; longitude: number | null }) {
  const { isLoaded, loadError } = useGoogleMapsLoader();

  if (!import.meta.env.VITE_GOOGLE_MAPS_API_KEY || loadError) return null;
  if (!isLoaded) return <MapStatusNotice>Loading map…</MapStatusNotice>;
  if (latitude == null || longitude == null) {
    return <MapStatusNotice>Update your location to see it on the map.</MapStatusNotice>;
  }

  const position = { lat: latitude, lng: longitude };
  return (
    <GoogleMap
      mapContainerStyle={MAP_CONTAINER_STYLE}
      center={position}
      zoom={CAMPUS_MAP_DEFAULT_ZOOM}
      options={{
        streetViewControl: false,
        mapTypeControl: false,
        fullscreenControl: false,
        gestureHandling: "cooperative",
      }}
    >
      <Marker position={position} />
    </GoogleMap>
  );
}
