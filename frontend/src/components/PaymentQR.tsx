import React from 'react';
import { useEffect, useState } from 'react';
import { Button, CircularProgress, Typography, Box } from '@mui/material';
import QRCode from 'react-qr-code';
import generateUPIQR from '../api/payments';

interface PaymentQRProps {
  orderId: string;
  amount: number;
}

export default function PaymentQR({ orderId, amount }: PaymentQRProps) {
  const [qrData, setQrData] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initiatePayment = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Call the API function properly
        const data = await generateUPIQR.initiateUPIPayment({
          order_id: orderId,
          amount,
          customer_name: "Customer Name",      // Replace with actual name
          customer_phone: "Customer Phone"     // Replace with actual phone
        });
        setQrData(data.upi_intent_url);
      } catch (err) {
        console.error('Payment QR generation failed:', err);
        setError('Failed to generate payment QR. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    if (orderId && amount) {
      initiatePayment();
    }
  }, [orderId, amount]);

  if (error) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', p: 4 }}>
        <Typography color="error" variant="body1" gutterBottom>
          {error}
        </Typography>
        <Button 
          variant="outlined" 
          onClick={() => window.location.reload()}
          sx={{ mt: 2 }}
        >
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', p: 4 }}>
      {isLoading ? (
        <CircularProgress />
      ) : (
        <>
          <Typography variant="h6" gutterBottom>
            Scan to Pay ₹{amount}
          </Typography>
          {qrData && (
            <Box sx={{ my: 2 }}>
              <QRCode value={qrData} size={200} />
            </Box>
          )}
          {qrData && (
            <Button
              variant="contained"
              sx={{ mt: 2 }}
              href={qrData}
              target="_blank"
              rel="noopener noreferrer"
            >
              Open in UPI App
            </Button>
          )}
        </>
      )}
    </Box>
  );
}