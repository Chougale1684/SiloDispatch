import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

export interface Payment {
  id: string;
  order_id: string;
  amount: number;
  payment_method: 'upi' | 'cash' | 'card';
  status: 'pending' | 'completed' | 'failed' | 'refunded';
  transaction_id?: string;
  upi_reference?: string;
  cash_received?: boolean;
  created_at: string;
}

export interface UPIPaymentRequest {
  order_id: string;
  amount: number;
  customer_name: string;
  customer_phone: string;
  customer_email?: string;
}

export interface CashPaymentRequest {
  order_id: string;
  amount: number;
  received_by: string; // Driver ID
}

export interface PaymentVerification {
  payment_id: string;
  order_id: string;
}

/**
 * Initiate UPI payment and get QR code/intent
 */
export const initiateUPIPayment = async (
  data: UPIPaymentRequest
): Promise<{
  qr_code_url: string;
  upi_intent_url: string;
  payment_id: string;
}> => {
  const response = await axios.post<{ qr_code_url: string; upi_intent_url: string; payment_id: string }>(
    `${API_BASE}/payments/upi`,
    data
  );
  return response.data;
};

/**
 * Record cash payment
 */
export const recordCashPayment = async (
  data: CashPaymentRequest
): Promise<Payment> => {
  const response = await axios.post<Payment>(`${API_BASE}/payments/cash`, data);
  return response.data;
};

/**
 * Verify payment status
 */
export const verifyPayment = async (
  paymentId: string
): Promise<{
  status: Payment['status'];
  transaction_details: any;
}> => {
  const response = await axios.get<{ status: "pending" | "completed" | "failed" | "refunded"; transaction_details: any }>(
    `${API_BASE}/payments/${paymentId}/verify`
  );
  return response.data;
};

/**
 * Get payment history for an order
 */
export const getOrderPayments = async (
  orderId: string
): Promise<Payment[]> => {
  const response = await axios.get<Payment[]>(`${API_BASE}/orders/${orderId}/payments`);
  return response.data;
};

/**
 * Process refund
 */
export const processRefund = async (
  paymentId: string,
  amount?: number
): Promise<Payment> => {
  const response = await axios.post<Payment>(`${API_BASE}/payments/${paymentId}/refund`, {
    amount,
  });
  return response.data;
};

/**
 * Get driver's cash ledger
 */
export const getDriverCashLedger = async (
  driverId: string
): Promise<{
  current_balance: number;
  today_collections: number;
  pending_settlement: number;
}> => {
  const response = await axios.get<{ current_balance: number; today_collections: number; pending_settlement: number }>(
    `${API_BASE}/drivers/${driverId}/cash-ledger`
  );
  return response.data;
};

/**
 * Settle driver's cash
 */
export const settleDriverCash = async (
  driverId: string,
  amount: number
): Promise<{
  settlement_id: string;
  new_balance: number;
}> => {
  const response = await axios.post<{ settlement_id: string; new_balance: number }>(
    `${API_BASE}/settlements`,
    {
      driver_id: driverId,
      amount,
    }
  );
  return response.data;
};

/**
 * Handle payment webhook verification
 */
export const verifyWebhookSignature = (
  payload: any,
  signature: string,
  secret: string
): boolean => {
  // Implement your signature verification logic here
  // This is just a placeholder example
  const crypto = require('crypto');
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(JSON.stringify(payload))
    .digest('hex');
  return signature === expectedSignature;
};

export default {
  initiateUPIPayment,
  recordCashPayment,
  verifyPayment,
  getOrderPayments,
  processRefund,
  getDriverCashLedger,
  settleDriverCash,
  verifyWebhookSignature,
};