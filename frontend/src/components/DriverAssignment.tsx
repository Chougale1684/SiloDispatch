import React from 'react';
import { useState } from 'react';
import { MenuItem, Select, Button } from '@mui/material';
import { assignDriver } from '../api/drivers';
import { useMutation } from '@tanstack/react-query';

interface DriverAssignmentProps {
  batchId: string;
  onAssignSuccess?: () => void;
}

export default function DriverAssignment({ batchId, onAssignSuccess }: DriverAssignmentProps) {
  const [driverId, setDriverId] = useState('');
  
  // Correct type parameters for useMutation:
  // 1. Return type (void in this case since assignDriver doesn't return anything)
  // 2. Error type
  // 3. Variables type
  const { mutate } = useMutation<void, Error, { batchId: string; driverId: string }>({
    mutationFn: assignDriver,
    onSuccess: () => {
      // Optional: Add success handling
      console.log('Driver assigned successfully');
      onAssignSuccess?.();
    },
    onError: (error) => {
      // Optional: Add error handling
      console.error('Assignment failed:', error);
    }
  });

  const handleAssign = () => {
    mutate({ batchId, driverId }, { onSuccess: onAssignSuccess });
  };

  return (
    <div className="mt-4 flex items-center space-x-2">
      <Select
        value={driverId}
        onChange={(e) => setDriverId(e.target.value)}
        displayEmpty
        size="small"
      >
        <MenuItem value="">Select Driver</MenuItem>
        {/* Populate with available drivers */}
      </Select>
      <Button 
        variant="contained" 
        onClick={handleAssign}
        disabled={!driverId}
      >
        Assign
      </Button>
    </div>
  );
}