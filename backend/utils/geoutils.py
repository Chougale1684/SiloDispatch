from geopy.distance import geodesic

def calculate_route_distance(points: list[tuple[float, float]]) -> float:
    """
    Calculate the total distance (in kilometers) for a delivery route.

    Args:
        points (list): List of tuples (latitude, longitude).

    Returns:
        float: Total distance in kilometers.
    """
    total_distance = 0.0

    # Iterate over each consecutive pair of points
    for i in range(len(points) - 1):
        segment_distance = geodesic(points[i], points[i + 1]).km
        total_distance += segment_distance

    return total_distance


# Example usage
if __name__ == "__main__":
    delivery_points = [
        (12.9716, 77.5946),  # Bangalore
        (13.0827, 80.2707),  # Chennai
        (11.0168, 76.9558)   # Coimbatore
    ]

    total_km = calculate_route_distance(delivery_points)
    print(f"Total delivery route distance: {total_km:.2f} km")
