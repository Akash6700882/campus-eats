import math

from app.models.delivery import DeliveryPartner

_EARTH_RADIUS_METERS = 6_371_000


def _distance_meters(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * _EARTH_RADIUS_METERS * math.asin(math.sqrt(a))


def find_nearest_partner(
    partners: list[DeliveryPartner], latitude: float, longitude: float
) -> DeliveryPartner | None:
    """Pick the available partner closest to `latitude`/`longitude` (typically
    the delivery address). Partners without a known location are excluded by
    the repository query before this is called."""
    if not partners:
        return None
    return min(
        partners,
        key=lambda p: _distance_meters(p.current_latitude, p.current_longitude, latitude, longitude),
    )
