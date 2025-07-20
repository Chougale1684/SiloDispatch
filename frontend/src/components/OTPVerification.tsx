import React from 'react';
import { useState } from 'react';
import { Button, TextField, Dialog, DialogActions, DialogContent, DialogTitle } from '@mui/material';
import { verifyDeliveryOTP } from '../api/orders';
import { useMutation } from '@tanstack/react-query';

export default function OTPVerification({ deliveryId, open, onClose }) {
  const [otp, setOtp] = useState('');
  const { mutate, isPending } = useMutation<
    { success: boolean; payment_unlocked: boolean }, // mutation result
    Error,                                          // error type
    { deliveryId: string; otp: string }             // variables type
  >({
    mutationFn: ({ deliveryId, otp }) => verifyDeliveryOTP(deliveryId, otp)
  });

  const handleVerify = () => {
    mutate({ deliveryId, otp }, { onSuccess: () => onClose(true) });
  };

  return (
    <Dialog open={open} onClose={() => onClose(false)}>
      <DialogTitle>OTP Verification</DialogTitle>
      <DialogContent>
        <TextField
          autoFocus
          margin="dense"
          label="Enter 6-digit OTP"
          type="text"
          fullWidth
          variant="standard"
          value={otp}
          onChange={(e) => setOtp(e.target.value)}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={() => onClose(false)}>Cancel</Button>
        <Button 
          onClick={handleVerify}
          disabled={otp.length !== 6 || isPending}
        >
          Verify
        </Button>
      </DialogActions>
    </Dialog>
  );
}