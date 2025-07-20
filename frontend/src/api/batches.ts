import axios from 'axios';
import { Order } from '../api/orders'; // adjust the path if needed

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

export const getTodayBatches = async () => {
  const response = await axios.get<{ batches: any[] }>(`${API_BASE}/batches/today`);
  return response.data.batches;
};

export const generateBatches = async () => {
  const response = await axios.post(`${API_BASE}/batches/create`, {
    algorithm: 'kmeans',
    max_weight: 25,
    max_orders: 30
  });
  return response.data;
};

export const assignDriver = async ({ batchId, driverId }) => {
  await axios.post(`${API_BASE}/batches/${batchId}/assign`, { driverId });
};

export const getBatchOrders = async (batchId: string): Promise<Order[]> => {
  const response = await axios.get<Order[]>(`/batches/${batchId}/orders`);
  return response.data;
};