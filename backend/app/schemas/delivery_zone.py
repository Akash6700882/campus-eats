import json
import uuid

from pydantic import BaseModel, field_validator
from shapely.errors import ShapelyError
from shapely.geometry import shape


class DeliveryZoneResponse(BaseModel):
    id: uuid.UUID
    name: str
    polygon_geojson: str
    is_active: bool

    @staticmethod
    def from_zone(zone) -> "DeliveryZoneResponse":
        return DeliveryZoneResponse(
            id=zone.id, name=zone.name, polygon_geojson=zone.polygon_geojson, is_active=zone.is_active
        )


class DeliveryZoneUpdateRequest(BaseModel):
    name: str
    polygon_geojson: str

    @field_validator("polygon_geojson")
    @classmethod
    def validate_polygon(cls, value: str) -> str:
        try:
            geom = shape(json.loads(value))
        except (ValueError, TypeError, ShapelyError) as exc:
            raise ValueError("polygon_geojson must be valid GeoJSON") from exc
        if geom.geom_type != "Polygon" or not geom.is_valid:
            raise ValueError("polygon_geojson must describe a single valid, non-self-intersecting Polygon")
        return value
