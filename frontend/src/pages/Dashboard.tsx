import { useQuery } from '@tanstack/react-query';
import React from 'react';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';

// API function - should be in a separate file (../api/orders.js)
export const fetchDashboardStats = async () => {
  // Example: fetch from your backend
  const res = await fetch('/api/stats');
  if (!res.ok) {
    throw new Error('Failed to fetch dashboard stats');
  }
  return res.json();
};

// Dashboard component
export function DashboardStats() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: fetchDashboardStats,
  });

  if (error) {
    return (
      <Paper sx={{ p: 2 }}>
        <Typography color="error">
          Error loading dashboard stats: {error.message}
        </Typography>
      </Paper>
    );
  }

  const cardStyle = {
    p: 2,
    textAlign: 'center',
    minHeight: 120,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center'
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Delivery Dashboard
      </Typography>
      
      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
          <Box sx={{ flex: '1 1 250px' }}>
            <Paper sx={cardStyle}>
              <Typography variant="h6" gutterBottom>
                Pending Orders
              </Typography>
              <Typography variant="h3" color="primary">
                {data?.pendingOrders || 0}
              </Typography>
            </Paper>
          </Box>
          
          <Box sx={{ flex: '1 1 250px' }}>
            <Paper sx={cardStyle}>
              <Typography variant="h6" gutterBottom>
                Completed Orders
              </Typography>
              <Typography variant="h3" sx={{ color: 'success.main' }}>
                {data?.completedOrders || 0}
              </Typography>
            </Paper>
          </Box>
          
          <Box sx={{ flex: '1 1 250px' }}>
            <Paper sx={cardStyle}>
              <Typography variant="h6" gutterBottom>
                Total Revenue
              </Typography>
              <Typography variant="h3" color="secondary">
                ${data?.totalRevenue || 0}
              </Typography>
            </Paper>
          </Box>
          
          <Box sx={{ flex: '1 1 250px' }}>
            <Paper sx={cardStyle}>
              <Typography variant="h6" gutterBottom>
                Active Drivers
              </Typography>
              <Typography variant="h3" sx={{ color: 'info.main' }}>
                {data?.activeDrivers || 0}
              </Typography>
            </Paper>
          </Box>
        </Box>
      )}
    </Box>
  );
}

const Dashboard: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body1">
        Welcome to the delivery management system
      </Typography>
    </Box>
  );
};

export default Dashboard;