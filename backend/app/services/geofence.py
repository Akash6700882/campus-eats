import json

from shapely.geometry import Point, shape


def point_in_zone(latitude: float, longitude: float, polygon_geojson: str) -> bool:
    """`polygon_geojson` is a GeoJSON Polygon (see DeliveryZone model) with
    [lng, lat] coordinate pairs, per the GeoJSON spec."""
    polygon = shape(json.loads(polygon_geojson))
    return polygon.contains(Point(longitude, latitude))
