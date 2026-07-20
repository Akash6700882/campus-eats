import { useCallback, useMemo, useRef, useState } from "react";
import { toast } from "sonner";
import { DrawingManager, GoogleMap, Polygon } from "@react-google-maps/api";
import { Button } from "@/components/ui/button";
import { PageSpinner } from "@/components/PageSpinner";
import { MapStatusNotice } from "@/components/map/MapStatusNotice";
import { useGoogleMapsLoader } from "@/hooks/useGoogleMapsLoader";
import { useDeliveryZone, useUpdateDeliveryZone } from "@/hooks/useDeliveryZone";
import { CAMPUS_CENTER, CAMPUS_MAP_DEFAULT_ZOOM, paddedCampusBounds } from "@/lib/campus";
import { pathToPolygonGeoJson, polygonGeoJsonToPath } from "@/lib/geo";

const MAP_CONTAINER_STYLE = { width: "100%", height: "420px", borderRadius: "0.75rem" };
const POLYGON_STYLE = { fillColor: "#f97316", fillOpacity: 0.15, strokeColor: "#f97316", strokeWeight: 2 };

export function DeliveryZoneEditor() {
  const { isLoaded, loadError } = useGoogleMapsLoader();
  const { data: zone, isLoading } = useDeliveryZone();
  const updateZone = useUpdateDeliveryZone();

  const polygonRef = useRef<google.maps.Polygon | null>(null);
  const [drawing, setDrawing] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [draftPath, setDraftPath] = useState<google.maps.LatLngLiteral[] | null>(null);

  const mapOptions = useMemo(
    () => ({
      restriction: { latLngBounds: paddedCampusBounds(0.01), strictBounds: false },
      streetViewControl: false,
      mapTypeControl: false,
      fullscreenControl: false,
    }),
    [],
  );

  const savedPath = useMemo(() => (zone ? polygonGeoJsonToPath(zone.polygon_geojson) : null), [zone]);
  const currentPath = draftPath ?? savedPath;

  const markDirty = useCallback(() => setDirty(true), []);

  function handlePolygonLoad(polygon: google.maps.Polygon) {
    polygonRef.current = polygon;
  }

  function handleDrawingComplete(polygon: google.maps.Polygon) {
    const path = polygon
      .getPath()
      .getArray()
      .map((p) => ({ lat: p.lat(), lng: p.lng() }));
    polygon.setMap(null); // hand the path to the editable Polygon below instead of keeping this one
    setDraftPath(path);
    setDirty(true);
    setDrawing(false);
  }

  function handleSave() {
    const path = polygonRef.current
      ?.getPath()
      .getArray()
      .map((p) => ({ lat: p.lat(), lng: p.lng() }));
    if (!path || path.length < 3) {
      toast.error("Draw at least a triangle before saving");
      return;
    }
    updateZone.mutate(
      { name: zone?.name ?? "IIT Guwahati Campus", polygon_geojson: pathToPolygonGeoJson(path) },
      {
        onSuccess: () => {
          setDirty(false);
          setDraftPath(null);
        },
      },
    );
  }

  function handleReset() {
    setDraftPath(null);
    setDirty(false);
  }

  if (!import.meta.env.VITE_GOOGLE_MAPS_API_KEY) {
    return (
      <MapStatusNotice>Set VITE_GOOGLE_MAPS_API_KEY in frontend/.env to edit the delivery zone visually.</MapStatusNotice>
    );
  }
  if (loadError) return <MapStatusNotice>Couldn&apos;t load the map.</MapStatusNotice>;
  if (isLoading || !isLoaded) return <PageSpinner />;

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm text-muted-foreground">
          Drag the boundary&apos;s points to adjust it, or draw a completely new shape.
        </p>
        <div className="flex gap-2">
          <Button type="button" variant="outline" size="sm" onClick={() => setDrawing(true)} disabled={drawing}>
            Draw new boundary
          </Button>
          <Button type="button" variant="outline" size="sm" onClick={handleReset} disabled={!dirty}>
            Reset
          </Button>
          <Button type="button" size="sm" onClick={handleSave} disabled={!dirty || updateZone.isPending}>
            Save changes
          </Button>
        </div>
      </div>

      <GoogleMap
        mapContainerStyle={MAP_CONTAINER_STYLE}
        center={currentPath?.[0] ?? CAMPUS_CENTER}
        zoom={CAMPUS_MAP_DEFAULT_ZOOM}
        options={mapOptions}
      >
        {drawing && (
          <DrawingManager
            options={{ drawingControl: false, polygonOptions: POLYGON_STYLE }}
            drawingMode={window.google.maps.drawing.OverlayType.POLYGON}
            onPolygonComplete={handleDrawingComplete}
          />
        )}
        {!drawing && currentPath && (
          <Polygon
            path={currentPath}
            editable
            draggable
            onLoad={handlePolygonLoad}
            onEdit={markDirty}
            onDragEnd={markDirty}
            options={POLYGON_STYLE}
          />
        )}
      </GoogleMap>

      {zone && (
        <p className="text-xs text-muted-foreground">
          Currently saved as &quot;{zone.name}&quot; ({(savedPath?.length ?? 1) - 1} points).
        </p>
      )}
    </div>
  );
}
