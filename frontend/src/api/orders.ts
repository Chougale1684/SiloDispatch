import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

export interface Order {
  id: string;
  customer_name: string;
  customer_phone: string;
  customer_address: string;
  pincode: string;
  latitude: number;
  longitude: number;
  items: Array<{
    name: string;
    quantity: number;
    price: number;
    weight: number;
  }>;
  total_weight: number;
  total_amount: number;
  status: 'pending' | 'batched' | 'assigned' | 'in_transit' | 'delivered' | 'cancelled';
  payment_method: 'upi' | 'cash' | 'prepaid';
  payment_status: 'pending' | 'paid' | 'failed';
  batch_id?: string;
  driver_id?: string;
  created_at: string;
}

export interface CreateOrderDto {
  customer_name: string;
  customer_phone: string;
  customer_address: string;
  pincode: string;
  latitude: number;
  longitude: number;
  items: Array<{
    name: string;
    quantity: number;
    price: number;
    weight: number;
  }>;
  total_weight: number;
  total_amount: number;
  payment_method: 'upi' | 'cash' | 'prepaid';
  delivery_slot?: string;
}

export interface UpdateOrderDto {
  customer_name?: string;
  customer_phone?: string;
  customer_address?: string;
  status?: Order['status'];
  payment_status?: Order['payment_status'];
}

/**
 * Fetch all orders with optional filters
 */
export const getOrders = async (params?: {
  status?: string;
  batch_id?: string;
  driver_id?: string;
}): Promise<Order[]> => {
  const response = await axios.get<Order[]>(`${API_BASE}/orders`, { params });
  return response.data;
};

/**
 * Create a new order
 */
export const createOrder = async (orderData: CreateOrderDto): Promise<Order> => {
  const response = await axios.post<Order>(`${API_BASE}/orders`, orderData);
  return response.data;
};

/**
 * Get order by ID
 */
export const getOrder = async (orderId: string): Promise<Order> => {
  const response = await axios.get<Order>(`${API_BASE}/orders/${orderId}`);
  return response.data;
};

/**
 * Update order
 */
export const updateOrder = async (
  orderId: string,
  updateData: UpdateOrderDto
): Promise<Order> => {
  const response = await axios.patch<Order>(`${API_BASE}/orders/${orderId}`, updateData);
  return response.data;
};

/**
 * Delete order
 */
export const deleteOrder = async (orderId: string): Promise<void> => {
  await axios.delete(`${API_BASE}/orders/${orderId}`);
};

/**
 * Import orders from CSV
 */
export const importOrdersCSV = async (file: File): Promise<{
  orders_created: number;
  errors: string[];
}> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await axios.post<{ orders_created: number; errors: string[] }>(
    `${API_BASE}/orders/import-csv`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};

/**
 * Mark order as delivered
 */
export const markDelivered = async (orderId: string): Promise<Order> => {
  const response = await axios.post<Order>(`${API_BASE}/orders/${orderId}/delivered`);
  return response.data;
};

/**
 * Verify OTP for delivery
 */
export const verifyDeliveryOTP = async (
  orderId: string,
  otp: string
): Promise<{ success: boolean; payment_unlocked: boolean }> => {
  const response = await axios.post<{ success: boolean; payment_unlocked: boolean }>(
    `${API_BASE}/orders/${orderId}/verify-otp`,
    { otp }
  );
  return response.data;
};

/**
 * Get orders for a specific batch
 */
export const getBatchOrders = async (batchId: string): Promise<Order[]> => {
  const response = await axios.get<Order[]>(`${API_BASE}/batches/${batchId}/orders`);
  return response.data;
};

/**
 * Get today's pending orders
 */
export const getTodayPendingOrders = async (): Promise<Order[]> => {
  const response = await axios.get<Order[]>(`${API_BASE}/orders/today/pending`);
  return response.data;
};

export default {
  getOrders,
  createOrder,
  getOrder,
  updateOrder,
  deleteOrder,
  importOrdersCSV,
  markDelivered,
  verifyDeliveryOTP,
  getBatchOrders,
  getTodayPendingOrders,
};