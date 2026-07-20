import { useCallback, useMemo } from "react";
import { GoogleMap, Marker, Polygon } from "@react-google-maps/api";
import { useGoogleMapsLoader } from "@/hooks/useGoogleMapsLoader";
import { useDeliveryZone } from "@/hooks/useDeliveryZone";
import { CAMPUS_CENTER, CAMPUS_MAP_DEFAULT_ZOOM, paddedCampusBounds } from "@/lib/campus";
import { polygonGeoJsonToPath } from "@/lib/geo";
import { MapStatusNotice } from "@/components/map/MapStatusNotice";

const MAP_CONTAINER_STYLE = { width: "100%", height: "260px", borderRadius: "0.75rem" };

export function CampusMapPicker({
  value,
  onChange,
}: {
  value: { latitude: number; longitude: number } | null;
  onChange: (coords: { latitude: number; longitude: number }) => void;
}) {
  const { isLoaded, loadError } = useGoogleMapsLoader();
  const { data: zone } = useDeliveryZone();

  const mapOptions = useMemo(
    () => ({
      restriction: { latLngBounds: paddedCampusBounds(), strictBounds: true },
      minZoom: 15,
      streetViewControl: false,
      mapTypeControl: false,
      fullscreenControl: false,
    }),
    [],
  );

  const zonePath = useMemo(() => (zone ? polygonGeoJsonToPath(zone.polygon_geojson) : null), [zone]);

  const markerPosition = value ? { lat: value.latitude, lng: value.longitude } : CAMPUS_CENTER;

  const handlePick = useCallback(
    (position: google.maps.LatLng | null) => {
      if (!position) return;
      onChange({ latitude: position.lat(), longitude: position.lng() });
    },
    [onChange],
  );

  if (!import.meta.env.VITE_GOOGLE_MAPS_API_KEY) {
    return <MapStatusNotice>Map picker isn&apos;t configured — use the location button below instead.</MapStatusNotice>;
  }
  if (loadError) {
    return <MapStatusNotice>Couldn&apos;t load the map — use the location button below instead.</MapStatusNotice>;
  }
  if (!isLoaded) {
    return <MapStatusNotice>Loading map…</MapStatusNotice>;
  }

  return (
    <GoogleMap
      mapContainerStyle={MAP_CONTAINER_STYLE}
      center={markerPosition}
      zoom={CAMPUS_MAP_DEFAULT_ZOOM}
      options={mapOptions}
      onClick={(e) => handlePick(e.latLng)}
    >
      {zonePath && (
        <Polygon
          path={zonePath}
          options={{
            fillColor: "#f97316",
            fillOpacity: 0.08,
            strokeColor: "#f97316",
            strokeOpacity: 0.6,
            strokeWeight: 2,
            clickable: false,
          }}
        />
      )}
      <Marker
        position={markerPosition}
        draggable
        onDragEnd={(e) => handlePick(e.latLng)}
      />
    </GoogleMap>
  );
}
