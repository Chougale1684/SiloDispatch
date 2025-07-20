// import axios from 'axios';

// const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';


// interface Driver {
//   id: string;
//   name: string;
//   phone: string;
//   vehicle_type: string;
//   vehicle_number: string;
//   status: 'available' | 'on_delivery' | 'offline';
//   current_location?: {
//     lat: number;
//     lng: number;
//   };
//   cash_in_hand?: number;
// }

// interface AssignmentData {
//   batchId: string;
//   driverId: string;
// }

// interface LocationUpdate {
//   driverId: string;
//   lat: number;
//   lng: number;
// }

// interface Settlement {
//   driverId: string;
//   amount: number;
// }

// /**
//  * Fetch all available drivers
//  */
// export const getDrivers = async (): Promise<Driver[]> => {
//   const response = await axios.get<Driver[]>(`${API_BASE}/drivers`);
//   return response.data;
// };

// /**
//  * Assign a driver to a batch
//  */
// export const assignDriver = async (data: AssignmentData): Promise<void> => {
//   await axios.post(`${API_BASE}/batches/${data.batchId}/assign`, {
//     driver_id: data.driverId
//   });
// };

// /**
//  * Update driver's current location
//  */
// export const updateDriverLocation = async (data: LocationUpdate): Promise<void> => {
//   await axios.post(`${API_BASE}/drivers/${data.driverId}/location`, {
//     lat: data.lat,
//     lng: data.lng
//   });
// };

// /**
//  * Get driver's current assigned batch
//  */
// export const getDriverBatch = async (driverId: string): Promise<any> => {
//   const response = await axios.get(`${API_BASE}/drivers/${driverId}/batch`);
//   return response.data;
// };

// /**
//  * Mark driver as arrived and generate OTP
//  */
// export const markArrived = async (deliveryId: string): Promise<{ otp: string }> => {
//   const response = await axios.post<{ otp: string }>(`${API_BASE}/deliveries/${deliveryId}/arrived`);
//   return response.data;
// };

// /**
//  * Get driver's cash ledger
//  */
// export const getDriverLedger = async (driverId: string): Promise<{ balance: number }> => {
//   const response = await axios.get<{ balance: number }>(`${API_BASE}/drivers/${driverId}/ledger`);
//   return response.data;
// };

// /**
//  * Settle driver's cash
//  */
// export const settleDriverCash = async (data: Settlement): Promise<void> => {
//   await axios.post(`${API_BASE}/settlements`, data);
// };

// /**
//  * Get driver's delivery history
//  */
// export const getDriverHistory = async (driverId: string, days: number = 7): Promise<any[]> => {
//   const response = await axios.get<any[]>(`${API_BASE}/drivers/${driverId}/history?days=${days}`);
//   return response.data;
// };

// /**
//  * Create a new driver
//  */
// export const createDriver = async (driverData: Omit<Driver, 'id'>): Promise<Driver> => {
//   const response = await axios.post<Driver>(`${API_BASE}/drivers`, driverData);
//   return response.data;
// };

// /**
//  * Update driver status
//  */
// export const updateDriverStatus = async (driverId: string, status: Driver['status']): Promise<void> => {
//   await axios.patch(`${API_BASE}/drivers/${driverId}/status`, { status });
// };

// /**
//  * Get real-time driver locations
//  */
// export const getLiveDriverLocations = async (): Promise<Record<string, { lat: number; lng: number }>> => {
//   const response = await axios.get<Record<string, { lat: number; lng: number }>>(`${API_BASE}/drivers/locations`);
//   return response.data;
// };

// /**
//  * Emergency alert endpoint
//  */
// export const sendEmergencyAlert = async (driverId: string): Promise<void> => {
//   await axios.post(`${API_BASE}/drivers/${driverId}/emergency`);
// };

// export default {
//   getDrivers,
//   assignDriver,
//   updateDriverLocation,
//   getDriverBatch,
//   markArrived,
//   getDriverLedger,
//   settleDriverCash,
//   getDriverHistory,
//   createDriver,
//   updateDriverStatus,
//   getLiveDriverLocations,
//   sendEmergencyAlert
// };

import axios from 'axios';

interface Driver {
  id: string;
  name: string;
  email: string;
  phone: string;
  licenseNumber: string;
  vehicleType: string;
  status: 'active' | 'inactive' | 'on_leave';
  createdAt: string;
}

export const fetchDrivers = async (): Promise<Driver[]> => {
  const response = await axios.get<Driver[]>('/api/drivers');
  return response.data;
};

export const deleteDriver = async (id: string): Promise<void> => {
  await axios.delete(`/api/drivers/${id}`);
};
