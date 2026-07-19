import json

from app.services.geofence import point_in_zone

# Small square: lng in [10, 11], lat in [10, 11]
SQUARE = json.dumps(
    {
        "type": "Polygon",
        "coordinates": [[[10, 10], [11, 10], [11, 11], [10, 11], [10, 10]]],
    }
)


def test_point_inside_zone():
    assert point_in_zone(latitude=10.5, longitude=10.5, polygon_geojson=SQUARE) is True


def test_point_outside_zone():
    assert point_in_zone(latitude=20.0, longitude=20.0, polygon_geojson=SQUARE) is False


def test_point_just_outside_boundary():
    assert point_in_zone(latitude=10.5, longitude=12.0, polygon_geojson=SQUARE) is False
