import math

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the great-circle distance between two GPS points in meters.
    """
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)

def is_within_geofence(shop_lat: float, shop_lon: float,
                       inspector_lat: float, inspector_lon: float,
                       max_distance_meters: float = 150.0) -> tuple[bool, float]:
    """
    Validates if inspector is within shop radius.
    """
    dist = calculate_haversine_distance(shop_lat, shop_lon, inspector_lat, inspector_lon)
    return (dist <= max_distance_meters), dist
