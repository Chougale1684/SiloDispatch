# generate_sample_data.py
import csv
import json
import random
import uuid
from datetime import datetime, timedelta

# Bangalore area pincodes with approximate coordinates
BANGALORE_PINCODES = [
    {"pincode": "560001", "area": "Bangalore City", "lat": 12.9716, "lon": 77.5946},
    {"pincode": "560002", "area": "Bangalore City", "lat": 12.9750, "lon": 77.5980},
    {"pincode": "560003", "area": "Bangalore City", "lat": 12.9800, "lon": 77.6000},
    {"pincode": "560004", "area": "Bangalore City", "lat": 12.9650, "lon": 77.5900},
    {"pincode": "560005", "area": "Bangalore City", "lat": 12.9700, "lon": 77.6050},
    {"pincode": "560010", "area": "Rajajinagar", "lat": 12.9900, "lon": 77.5550},
    {"pincode": "560020", "area": "Rajajinagar", "lat": 12.9950, "lon": 77.5600},
    {"pincode": "560040", "area": "Jayanagar", "lat": 12.9250, "lon": 77.5833},
    {"pincode": "560041", "area": "Jayanagar", "lat": 12.9300, "lon": 77.5900},
    {"pincode": "560050", "area": "Basavanagudi", "lat": 12.9400, "lon": 77.5700},
    {"pincode": "560070", "area": "Koramangala", "lat": 12.9352, "lon": 77.6245},
    {"pincode": "560076", "area": "Koramangala", "lat": 12.9400, "lon": 77.6300},
    {"pincode": "560095", "area": "Koramangala", "lat": 12.9450, "lon": 77.6350},
    {"pincode": "560100", "area": "Indiranagar", "lat": 12.9784, "lon": 77.6408},
    {"pincode": "560008", "area": "Malleshwaram", "lat": 13.0039, "lon": 77.5749},
    {"pincode": "560046", "area": "Malleshwaram", "lat": 13.0100, "lon": 77.5800},
    {"pincode": "560017", "area": "Seshadripuram", "lat": 12.9900, "lon": 77.5700},
    {"pincode": "560018", "area": "Seshadripuram", "lat": 12.9950, "lon": 77.5750},
    {"pincode": "560025", "area": "Banashankari", "lat": 12.9180, "lon": 77.5500},
    {"pincode": "560070", "area": "Banashankari", "lat": 12.9200, "lon": 77.5550},
    {"pincode": "562159", "area": "Ramanagara", "lat": 12.7209, "lon": 77.2833},
    {"pincode": "571401", "area": "Mandya", "lat": 12.5214, "lon": 76.8956},
    {"pincode": "570001", "area": "Mysore", "lat": 12.2958, "lon": 76.6394},
    {"pincode": "573201", "area": "Hassan", "lat": 13.0072, "lon": 76.1004},
    {"pincode": "577001", "area": "Davangere", "lat": 14.4644, "lon": 75.9170},
]

# Sample customer names
CUSTOMER_NAMES = [
    "Dairy Farm A", "Dairy Farm B", "Dairy Farm C", "Gowri Dairy", "Lakshmi Dairy",
    "Venkatesh Dairy", "Manjunath Dairy", "Ravi Dairy", "Suresh Dairy", "Ramesh Dairy",
    "Nagaraj Dairy", "Krishnamurthy Dairy", "Srinivas Dairy", "Govind Dairy", "Mohan Dairy",
    "Sharath Dairy", "Prakash Dairy", "Vinod Dairy", "Ashok Dairy", "Rajesh Dairy",
    "Mahesh Dairy", "Girish Dairy", "Sundar Dairy", "Naveen Dairy", "Kiran Dairy",
    "Yogesh Dairy", "Pavan Dairy", "Sandeep Dairy", "Deepak Dairy", "Anand Dairy"
]

# Sample addresses
ADDRESSES = [
    "123 Farm Road", "456 Village Center", "789 Rural Road", "321 Dairy Lane",
    "654 Cattle Street", "987 Milk Road", "147 Farm House", "258 Village Square",
    "369 Rural Junction", "741 Dairy Complex", "852 Farm Estate", "963 Village Park",
    "159 Rural Plaza", "357 Dairy Center", "753 Farm Valley", "951 Village Heights",
    "357 Rural Gardens", "159 Dairy Hills", "753 Farm Meadows", "951 Village Grove"
]

# Sample items
ITEMS = [
    {"name": "Cattle Feed Premium", "unit_weight": 25},
    {"name": "Cattle Feed Standard", "unit_weight": 25},
    {"name": "Buffalo Feed", "unit_weight": 30},
    {"name": "Dairy Supplement", "unit_weight": 5},
    {"name": "Mineral Mixture", "unit_weight": 10},
    {"name": "Protein Pellets", "unit_weight": 20},
    {"name": "Hay Bales", "unit_weight": 15},
    {"name": "Silage Feed", "unit_weight": 50}
]

def generate_phone_number():
    """Generate a random Indian phone number"""
    return f"9{random.randint(100000000, 999999999)}"

def generate_order_items():
    """Generate random order items"""
    num_items = random.randint(1, 3)
    items = []
    
    for _ in range(num_items):
        item = random.choice(ITEMS)
        quantity = random.randint(1, 5)
        items.append({
            "name": item["name"],
            "quantity": quantity,
            "weight": item["unit_weight"]
        })
    
    return items

def calculate_order_total(items):
    """Calculate total weight and amount for items"""
    total_weight = sum(item["quantity"] * item["weight"] for item in items)
    
    # Price per kg varies by item type
    price_per_kg = {
        "Cattle Feed Premium": 30,
        "Cattle Feed Standard": 25,
        "Buffalo Feed": 28,
        "Dairy Supplement": 45,
        "Mineral Mixture": 35,
        "Protein Pellets": 40,
        "Hay Bales": 20,
        "Silage Feed": 18
    }
    
    total_amount = sum(item["quantity"] * item["weight"] * price_per_kg.get(item["name"], 25) for item in items)
    
    return total_weight, total_amount

def generate_delivery_status():
    """Generate random delivery status"""
    statuses = ["Pending", "In Transit", "Delivered", "Cancelled"]
    weights = [0.2, 0.3, 0.4, 0.1]  # More likely to be delivered
    return random.choices(statuses, weights=weights)[0]

def generate_order_date():
    """Generate random order date within last 6 months"""
    start_date = datetime.now() - timedelta(days=180)
    random_days = random.randint(0, 180)
    return start_date + timedelta(days=random_days)

def generate_delivery_date(order_date, status):
    """Generate delivery date based on order date and status"""
    if status == "Pending":
        return None
    elif status == "Cancelled":
        return None
    else:
        # Delivery typically happens 1-3 days after order
        delivery_days = random.randint(1, 3)
        return order_date + timedelta(days=delivery_days)

def generate_customers(num_customers=50):
    """Generate customer data"""
    customers = []
    
    for i in range(num_customers):
        location = random.choice(BANGALORE_PINCODES)
        customer = {
            "customer_id": f"CUST{i+1:04d}",
            "name": random.choice(CUSTOMER_NAMES),
            "phone": generate_phone_number(),
            "address": random.choice(ADDRESSES),
            "pincode": location["pincode"],
            "area": location["area"],
            "latitude": location["lat"] + random.uniform(-0.01, 0.01),  # Add some variation
            "longitude": location["lon"] + random.uniform(-0.01, 0.01),
            "registration_date": generate_order_date().strftime("%Y-%m-%d")
        }
        customers.append(customer)
    
    return customers

def generate_orders(customers, num_orders=200):
    """Generate order data"""
    orders = []
    
    for i in range(num_orders):
        customer = random.choice(customers)
        order_date = generate_order_date()
        status = generate_delivery_status()
        delivery_date = generate_delivery_date(order_date, status)
        
        items = generate_order_items()
        total_weight, total_amount = calculate_order_total(items)
        
        order = {
            "order_id": f"ORD{i+1:06d}",
            "customer_id": customer["customer_id"],
            "customer_name": customer["name"],
            "order_date": order_date.strftime("%Y-%m-%d"),
            "delivery_date": delivery_date.strftime("%Y-%m-%d") if delivery_date else "",
            "status": status,
            "items": json.dumps(items),
            "total_weight_kg": total_weight,
            "total_amount": total_amount,
            "delivery_address": customer["address"],
            "pincode": customer["pincode"],
            "area": customer["area"],
            "latitude": customer["latitude"],
            "longitude": customer["longitude"]
        }
        orders.append(order)
    
    return orders

def generate_delivery_routes(orders):
    """Generate delivery route data"""
    routes = []
    delivered_orders = [order for order in orders if order["status"] == "Delivered"]
    
    # Group orders by delivery date and area for route optimization
    route_groups = {}
    for order in delivered_orders:
        key = f"{order['delivery_date']}_{order['area']}"
        if key not in route_groups:
            route_groups[key] = []
        route_groups[key].append(order)
    
    route_id = 1
    for key, orders_group in route_groups.items():
        if len(orders_group) > 0:
            delivery_date, area = key.split("_", 1)
            total_weight = sum(order["total_weight_kg"] for order in orders_group)
            total_orders = len(orders_group)
            
            route = {
                "route_id": f"ROUTE{route_id:04d}",
                "delivery_date": delivery_date,
                "area": area,
                "total_orders": total_orders,
                "total_weight_kg": total_weight,
                "driver_name": f"Driver {random.randint(1, 20)}",
                "vehicle_number": f"KA{random.randint(10, 99)}{random.choice(['A', 'B', 'C'])}{random.randint(1000, 9999)}",
                "start_time": f"{random.randint(8, 10)}:00",
                "estimated_duration_hours": min(8, max(2, total_orders * 0.5)),
                "order_ids": ",".join([order["order_id"] for order in orders_group])
            }
            routes.append(route)
            route_id += 1
    
    return routes

def save_to_csv(data, filename, fieldnames):
    """Save data to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def main():
    """Main function to generate all sample data"""
    print("Generating sample data for dairy feed delivery business...")
    
    # Generate customers
    print("Generating customers...")
    customers = generate_customers(50)
    customer_fieldnames = ["customer_id", "name", "phone", "address", "pincode", "area", 
                          "latitude", "longitude", "registration_date"]
    save_to_csv(customers, "customers.csv", customer_fieldnames)
    
    # Generate orders
    print("Generating orders...")
    orders = generate_orders(customers, 200)
    order_fieldnames = ["order_id", "customer_id", "customer_name", "order_date", 
                       "delivery_date", "status", "items", "total_weight_kg", 
                       "total_amount", "delivery_address", "pincode", "area", 
                       "latitude", "longitude"]
    save_to_csv(orders, "orders.csv", order_fieldnames)
    
    # Generate delivery routes
    print("Generating delivery routes...")
    routes = generate_delivery_routes(orders)
    route_fieldnames = ["route_id", "delivery_date", "area", "total_orders", 
                       "total_weight_kg", "driver_name", "vehicle_number", 
                       "start_time", "estimated_duration_hours", "order_ids"]
    save_to_csv(routes, "delivery_routes.csv", route_fieldnames)
    
    # Generate summary statistics
    print("\n=== SUMMARY STATISTICS ===")
    print(f"Total customers generated: {len(customers)}")
    print(f"Total orders generated: {len(orders)}")
    print(f"Total delivery routes generated: {len(routes)}")
    
    # Order status breakdown
    status_count = {}
    for order in orders:
        status = order["status"]
        status_count[status] = status_count.get(status, 0) + 1
    
    print("\nOrder Status Breakdown:")
    for status, count in status_count.items():
        print(f"  {status}: {count}")
    
    # Area distribution
    area_count = {}
    for customer in customers:
        area = customer["area"]
        area_count[area] = area_count.get(area, 0) + 1
    
    print("\nCustomer Area Distribution:")
    for area, count in sorted(area_count.items()):
        print(f"  {area}: {count}")
    
    print("\nFiles generated:")
    print("- customers.csv")
    print("- orders.csv")
    print("- delivery_routes.csv")
    print("\nSample data generation completed!")

if __name__ == "__main__":
    main()