import React from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Button,
  Stack,
  Divider,
  CircularProgress
} from '@mui/material';
import { Download, Refresh } from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { fetchSettlementReport } from '../api/settlements';

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

const SettlementReport: React.FC = () => {
  const { data: settlements, isLoading, isError, refetch } = useQuery<SettlementItem[]>({
    queryKey: ['settlements'],
    queryFn: fetchSettlementReport
  });

  const handleDownload = () => {
    // Implement download logic here
    console.log('Downloading settlement report...');
  };

  const totalAmount = settlements?.reduce((sum, item) => sum + item.amount, 0) || 0;
  const totalFees = settlements?.reduce((sum, item) => sum + item.fees, 0) || 0;
  const totalTax = settlements?.reduce((sum, item) => sum + item.tax, 0) || 0;
  const totalNet = settlements?.reduce((sum, item) => sum + item.netAmount, 0) || 0;

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (isError) {
    return (
      <Box textAlign="center" p={4}>
        <Typography color="error" gutterBottom>
          Failed to load settlement report
        </Typography>
        <Button 
          variant="outlined" 
          startIcon={<Refresh />}
          onClick={() => refetch()}
        >
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" component="h2">
          Settlement Report
        </Typography>
        <Stack direction="row" spacing={2}>
          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={handleDownload}
          >
            Download
          </Button>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={() => refetch()}
          >
            Refresh
          </Button>
        </Stack>
      </Stack>

      <TableContainer component={Paper} sx={{ mb: 3 }}>
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
              <TableCell>Date</TableCell>
              <TableCell>Order ID</TableCell>
              <TableCell align="right">Amount (₹)</TableCell>
              <TableCell align="right">Fees (₹)</TableCell>
              <TableCell align="right">Tax (₹)</TableCell>
              <TableCell align="right">Net Amount (₹)</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {settlements?.map((settlement) => (
              <TableRow key={settlement.id}>
                <TableCell>{new Date(settlement.date).toLocaleDateString()}</TableCell>
                <TableCell>{settlement.orderId}</TableCell>
                <TableCell align="right">{settlement.amount.toFixed(2)}</TableCell>
                <TableCell align="right">{settlement.fees.toFixed(2)}</TableCell>
                <TableCell align="right">{settlement.tax.toFixed(2)}</TableCell>
                <TableCell align="right">{settlement.netAmount.toFixed(2)}</TableCell>
                <TableCell>
                  <Box 
                    component="span" 
                    sx={{
                      px: 1,
                      py: 0.5,
                      borderRadius: 1,
                      backgroundColor: 
                        settlement.status === 'processed' ? '#e8f5e9' :
                        settlement.status === 'failed' ? '#ffebee' : '#fff8e1',
                      color: 
                        settlement.status === 'processed' ? '#2e7d32' :
                        settlement.status === 'failed' ? '#c62828' : '#f57f17',
                    }}
                  >
                    {settlement.status.charAt(0).toUpperCase() + settlement.status.slice(1)}
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Divider sx={{ my: 2 }} />

      <Stack direction="row" justifyContent="flex-end" spacing={4} sx={{ mt: 2 }}>
        <Box textAlign="right">
          <Typography variant="subtitle1">Total Amount:</Typography>
          <Typography variant="subtitle1">Total Fees:</Typography>
          <Typography variant="subtitle1">Total Tax:</Typography>
          <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>Net Settlement:</Typography>
        </Box>
        <Box textAlign="right">
          <Typography variant="subtitle1">₹{totalAmount.toFixed(2)}</Typography>
          <Typography variant="subtitle1">₹{totalFees.toFixed(2)}</Typography>
          <Typography variant="subtitle1">₹{totalTax.toFixed(2)}</Typography>
          <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>₹{totalNet.toFixed(2)}</Typography>
        </Box>
      </Stack>
    </Paper>
  );
};

export default SettlementReport;