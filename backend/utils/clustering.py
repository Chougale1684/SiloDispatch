# clustering.py
import math
import numpy as np
from sklearn.cluster import KMeans
from typing import List, Dict, Tuple
from models.models import Order
import uuid

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    return c * r

def calculate_cluster_center(orders: List[Order]) -> Tuple[float, float]:
    """Calculate the geographic center of a cluster of orders"""
    if not orders:
        return 0.0, 0.0
    
    lat_sum = sum(order.latitude for order in orders)
    lon_sum = sum(order.longitude for order in orders)
    
    return lat_sum / len(orders), lon_sum / len(orders)

def estimate_route_distance(orders: List[Order]) -> float:
    """Estimate total distance for a route using nearest neighbor approximation"""
    if len(orders) <= 1:
        return 0.0
    
    # Start from cluster center
    center_lat, center_lon = calculate_cluster_center(orders)
    
    # Calculate distances from center to all points and between points
    total_distance = 0.0
    visited = set()
    current_lat, current_lon = center_lat, center_lon
    
    while len(visited) < len(orders):
        min_distance = float('inf')
        next_order = None
        
        for order in orders:
            if order.id not in visited:
                dist = haversine_distance(current_lat, current_lon, order.latitude, order.longitude)
                if dist < min_distance:
                    min_distance = dist
                    next_order = order
        
        if next_order:
            total_distance += min_distance
            visited.add(next_order.id)
            current_lat, current_lon = next_order.latitude, next_order.longitude
    
    return total_distance

def simple_pincode_clustering(orders: List[Order], max_weight: float = 25.0, max_orders: int = 30) -> List[Dict]:
    """
    Simple clustering based on pincode proximity
    """
    if not orders:
        return []
    
    # Group orders by pincode first
    pincode_groups = {}
    for order in orders:
        if order.pincode not in pincode_groups:
            pincode_groups[order.pincode] = []
        pincode_groups[order.pincode].append(order)
    
    batches = []
    
    for pincode, pincode_orders in pincode_groups.items():
        # Split large pincode groups into smaller batches
        current_batch = []
        current_weight = 0.0
        
        for order in pincode_orders:
            # Check if adding this order would exceed limits
            if (len(current_batch) >= max_orders or 
                current_weight + order.total_weight > max_weight):
                
                # Create batch if it has orders
                if current_batch:
                    center_lat, center_lon = calculate_cluster_center(current_batch)
                    estimated_distance = estimate_route_distance(current_batch)
                    
                    batches.append({
                        'id': str(uuid.uuid4()),
                        'orders': current_batch,
                        'total_weight': current_weight,
                        'total_orders': len(current_batch),
                        'center_latitude': center_lat,
                        'center_longitude': center_lon,
                        'estimated_distance': estimated_distance,
                        'pincode': pincode
                    })
                
                # Start new batch
                current_batch = [order]
                current_weight = order.total_weight
            else:
                current_batch.append(order)
                current_weight += order.total_weight
        
        # Add remaining orders as a batch
        if current_batch:
            center_lat, center_lon = calculate_cluster_center(current_batch)
            estimated_distance = estimate_route_distance(current_batch)
            
            batches.append({
                'id': str(uuid.uuid4()),
                'orders': current_batch,
                'total_weight': current_weight,
                'total_orders': len(current_batch),
                'center_latitude': center_lat,
                'center_longitude': center_lon,
                'estimated_distance': estimated_distance,
                'pincode': pincode
            })
    
    return batches

def kmeans_clustering(orders: List[Order], max_weight: float = 25.0, max_orders: int = 30) -> List[Dict]:
    """
    Advanced clustering using K-means algorithm
    """
    if not orders:
        return []
    
    if len(orders) == 1:
        return simple_pincode_clustering(orders, max_weight, max_orders)
    
    # Prepare data for K-means
    coordinates = np.array([[order.latitude, order.longitude] for order in orders])
    weights = np.array([order.total_weight for order in orders])
    
    # Estimate optimal number of clusters
    # Start with pincode-based estimate
    unique_pincodes = len(set(order.pincode for order in orders))
    
    # Calculate based on weight and order constraints
    weight_based_clusters = math.ceil(sum(weights) / max_weight)
    order_based_clusters = math.ceil(len(orders) / max_orders)
    
    # Use the maximum to ensure constraints are met
    estimated_clusters = max(unique_pincodes, weight_based_clusters, order_based_clusters)
    
    # Ensure we don't have more clusters than orders
    n_clusters = min(estimated_clusters, len(orders))
    
    # Apply K-means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(coordinates)
    
    # Group orders by cluster
    clusters = {}
    for i, label in enumerate(cluster_labels):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(orders[i])
    
    # Post-process clusters to ensure constraints
    final_batches = []
    
    for cluster_orders in clusters.values():
        # Split large clusters that exceed constraints
        sub_batches = split_large_cluster(cluster_orders, max_weight, max_orders)
        final_batches.extend(sub_batches)
    
    return final_batches

def split_large_cluster(orders: List[Order], max_weight: float, max_orders: int) -> List[Dict]:
    """Split a cluster that exceeds weight or order limits"""
    if not orders:
        return []
    
    # Sort orders by weight (heaviest first) for better packing
    sorted_orders = sorted(orders, key=lambda x: x.total_weight, reverse=True)
    
    batches = []
    current_batch = []
    current_weight = 0.0
    
    for order in sorted_orders:
        # Check if adding this order would exceed limits
        if (len(current_batch) >= max_orders or 
            current_weight + order.total_weight > max_weight):
            
            # Create batch if it has orders
            if current_batch:
                center_lat, center_lon = calculate_cluster_center(current_batch)
                estimated_distance = estimate_route_distance(current_batch)
                
                batches.append({
                    'id': str(uuid.uuid4()),
                    'orders': current_batch,
                    'total_weight': current_weight,
                    'total_orders': len(current_batch),
                    'center_latitude': center_lat,
                    'center_longitude': center_lon,
                    'estimated_distance': estimated_distance
                })
            
            # Start new batch
            current_batch = [order]
            current_weight = order.total_weight
        else:
            current_batch.append(order)
            current_weight += order.total_weight
    
    # Add remaining orders as a batch
    if current_batch:
        center_lat, center_lon = calculate_cluster_center(current_batch)
        estimated_distance = estimate_route_distance(current_batch)
        
        batches.append({
            'id': str(uuid.uuid4()),
            'orders': current_batch,
            'total_weight': current_weight,
            'total_orders': len(current_batch),
            'center_latitude': center_lat,
            'center_longitude': center_lon,
            'estimated_distance': estimated_distance
        })
    
    return batches

def create_optimized_batches(orders: List[Order], algorithm: str = "kmeans", 
                           max_weight: float = 25.0, max_orders: int = 30) -> List[Dict]:
    """
    Main function to create optimized batches
    """
    if algorithm == "simple":
        return simple_pincode_clustering(orders, max_weight, max_orders)
    else:
        return kmeans_clustering(orders, max_weight, max_orders)

# Example usage and testing
if __name__ == "__main__":
    # Test with sample data
    sample_orders = [
        Order(id="1", customer_name="Farm A", pincode="560001", latitude=12.9716, longitude=77.5946, total_weight=20.0),
        Order(id="2", customer_name="Farm B", pincode="560001", latitude=12.9750, longitude=77.5980, total_weight=15.0),
        Order(id="3", customer_name="Farm C", pincode="560002", latitude=12.9800, longitude=77.6000, total_weight=10.0),
    ]
    
    batches = create_optimized_batches(sample_orders, algorithm="kmeans")
    
    for i, batch in enumerate(batches):
        print(f"Batch {i+1}: {batch['total_orders']} orders, {batch['total_weight']}kg, "
              f"Distance: {batch['estimated_distance']:.2f}km")