import React from 'react';
import { Card, CardContent, Typography, Button, Chip, Stack, Divider, Box } from '@mui/material';
import { useMutation } from '@tanstack/react-query';
import { assignDriver, getBatchOrders } from '../api/batches';
import { Order } from '../api/orders';
import DriverAssignment from './DriverAssignment';
import OrderList from './OrderList';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface Batch {
  id: string;
  created_at: string;
  status: 'pending' | 'assigned' | 'in_progress' | 'completed';
  current_weight: number;
  current_orders: number;
  estimated_distance?: number;
  driver_id?: string;
  driver_name?: string;
}

interface BatchCardProps {
  batch: Batch;
  refetchBatches: () => void;
}

const BatchCard: React.FC<BatchCardProps> = ({ batch, refetchBatches }) => {
  const navigate = useNavigate();
  const [expanded, setExpanded] = React.useState(false);
  const [orders, setOrders] = React.useState<Order[]>([]);

  const { mutate: fetchOrders } = useMutation<Order[], Error, void>({
    mutationFn: (): Promise<Order[]> => getBatchOrders(batch.id),
    onSuccess: (data) => {
      setOrders(data);
      setExpanded(!expanded);
    }
  });

  const handleViewDetails = () => {
    if (!expanded || orders.length === 0) {
      fetchOrders();
    } else {
      setExpanded(!expanded);
    }
  };

  const handleTrackBatch = () => {
    navigate(`/tracking/${batch.id}`);
  };

  const getStatusColor = () => {
    switch (batch.status) {
      case 'pending': return 'warning';
      case 'assigned': return 'info';
      case 'in_progress': return 'primary';
      case 'completed': return 'success';
      default: return 'default';
    }
  };

  return (
    <Card sx={{ mb: 2, boxShadow: 3 }}>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" component="div">
            Batch #{batch.id.slice(0, 8)}
          </Typography>
          <Chip 
            label={batch.status.replace('_', ' ')} 
            color={getStatusColor()}
            size="small"
          />
        </Stack>

        <Stack direction="row" spacing={2} sx={{ mt: 1, mb: 1 }}>
          <Typography variant="body2">
            <strong>{batch.current_orders}</strong> orders
          </Typography>
          <Typography variant="body2">
            <strong>{batch.current_weight} kg</strong>
          </Typography>
          {batch.estimated_distance && (
            <Typography variant="body2">
              <strong>{batch.estimated_distance} km</strong>
            </Typography>
          )}
        </Stack>

        {batch.driver_name && (
          <Typography variant="body2" sx={{ mb: 1 }}>
            Driver: <strong>{batch.driver_name}</strong>
          </Typography>
        )}

        <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
          <Button 
            variant="outlined" 
            size="small"
            onClick={handleViewDetails}
          >
            {expanded ? 'Hide Orders' : 'View Orders'}
          </Button>

          {batch.status !== 'completed' && (
            <Button 
              variant="contained" 
              size="small"
              onClick={handleTrackBatch}
            >
              Track
            </Button>
          )}
        </Stack>

        {!batch.driver_id && (
          <Box sx={{ mt: 2 }}>
            <DriverAssignment 
              batchId={batch.id} 
              onAssignSuccess={() => refetchBatches()} 
            />
          </Box>
        )}

        {expanded && orders.length > 0 && (
          <>
            <Divider sx={{ my: 2 }} />
            <OrderList orders={orders} />
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default BatchCard;