import axios from 'axios';

interface SettlementItem {
  id: string;
  date: string;
  orderId: string;
  amount: number;
  fees: number;
  tax: number;
  netAmount: number;
  status: 'pending' | 'processed' | 'failed';
}

interface Settlement {
  id: string;
  settlementDate: string;
  orderId: string;
  amount: number;
  fees: number;
  tax: number;
  netAmount: number;
  status: 'pending' | 'processed' | 'failed';
  paymentMethod: 'card' | 'upi' | 'netbanking' | 'wallet';
}

export const fetchSettlementReport = async (): Promise<SettlementItem[]> => {
  try {
    const response = await axios.get<SettlementItem[]>('/api/settlements');
    return response.data;
  } catch (error) {
    console.error('Error fetching settlement report:', error);
    throw new Error('Failed to fetch settlement report');
  }
};


export const fetchSettlements = async (): Promise<Settlement[]> => {
  const response = await axios.get<Settlement[]>('/api/settlements');
  return response.data;
};