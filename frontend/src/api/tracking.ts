import axios from 'axios';

interface TrackingStep {
  status: string;
  timestamp: string;
  location?: {
    lat: number;
    lng: number;
  };
  description?: string;
}

interface TrackingDetails {
  orderId: string;
  customerName: string;
  customerPhone: string;
  deliveryAddress: string;
  restaurantName: string;
  restaurantLocation: {
    lat: number;
    lng: number;
  };
  deliveryLocation: {
    lat: number;
    lng: number;
  };
  driverName: string;
  driverPhone: string;
  driverLocation: {
    lat: number;
    lng: number;
  };
  estimatedDeliveryTime: string;
  currentStatus: 'preparing' | 'picked_up' | 'on_the_way' | 'delivered' | 'cancelled';
  steps: TrackingStep[];
}

export const fetchTrackingDetails = async (orderId: string): Promise<TrackingDetails> => {
  const response = await axios.get<TrackingDetails>(`/api/tracking/${orderId}`);
  return response.data;
};