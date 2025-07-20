// frontend/src/components/EstimatedTimeArrival.tsx
import React from 'react';
import { Typography } from '@mui/material';

interface Props {
  eta: string;
  status: string;
}

const EstimatedTimeArrival: React.FC<Props> = ({ eta, status }) => (
  <Typography>
    ETA: {eta} ({status})
  </Typography>
);

export default EstimatedTimeArrival;
