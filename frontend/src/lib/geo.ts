/** GeoJSON Polygon coordinates are [lng, lat] pairs; Google Maps wants
 * {lat, lng} literals. Keep the conversion in one place. */
export function polygonGeoJsonToPath(polygonGeoJson: string): google.maps.LatLngLiteral[] {
  const geo = JSON.parse(polygonGeoJson) as { coordinates: [number, number][][] };
  return geo.coordinates[0].map(([lng, lat]) => ({ lat, lng }));
}

export function pathToPolygonGeoJson(path: google.maps.LatLngLiteral[]): string {
  const ring = path.map(({ lat, lng }): [number, number] => [lng, lat]);
  const [firstLng, firstLat] = ring[0];
  const [lastLng, lastLat] = ring[ring.length - 1];
  if (firstLng !== lastLng || firstLat !== lastLat) ring.push(ring[0]);
  return JSON.stringify({ type: "Polygon", coordinates: [ring] });
}
