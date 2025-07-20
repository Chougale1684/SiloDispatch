import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Container,
  Divider,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TextField,
  Typography
} from '@mui/material';
import {
  Download,
  Refresh,
  Search,
  DateRange
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { fetchSettlements } from '../api/settlements';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

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

const Settlements: React.FC = () => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [paymentMethodFilter, setPaymentMethodFilter] = useState<string>('all');
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);

  const { data: settlements, isLoading, isError, refetch } = useQuery<Settlement[]>({
    queryKey: ['settlements'],
    queryFn: fetchSettlements
  });

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleExport = () => {
    // Implement export logic here
    console.log('Exporting settlements data...');
  };

  const filteredSettlements = settlements?.filter(settlement => {
    const matchesSearch = 
      settlement.orderId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      settlement.id.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || settlement.status === statusFilter;
    const matchesPaymentMethod = paymentMethodFilter === 'all' || settlement.paymentMethod === paymentMethodFilter;
    
    const settlementDate = new Date(settlement.settlementDate);
    const matchesDateRange = 
      (!startDate || settlementDate >= startDate) && 
      (!endDate || settlementDate <= endDate);

    return matchesSearch && matchesStatus && matchesPaymentMethod && matchesDateRange;
  }) || [];

  const paginatedSettlements = filteredSettlements.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  const totalAmount = filteredSettlements.reduce((sum, item) => sum + item.amount, 0);
  const totalFees = filteredSettlements.reduce((sum, item) => sum + item.fees, 0);
  const totalTax = filteredSettlements.reduce((sum, item) => sum + item.tax, 0);
  const totalNet = filteredSettlements.reduce((sum, item) => sum + item.netAmount, 0);

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
          Failed to load settlements
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
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Container maxWidth="xl">
        <Stack spacing={3}>
          <Typography variant="h4" component="h1" gutterBottom>
            Settlement Transactions
          </Typography>

          <Card>
            <CardContent>
              <Stack 
                direction={{ xs: 'column', md: 'row' }} 
                spacing={2}
                alignItems="center"
                mb={3}
              >
                <TextField
                  variant="outlined"
                  size="small"
                  placeholder="Search by Order ID or Settlement ID"
                  InputProps={{
                    startAdornment: <Search color="action" sx={{ mr: 1 }} />
                  }}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  sx={{ width: 300 }}
                />

                <FormControl size="small" sx={{ minWidth: 180 }}>
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={statusFilter}
                    label="Status"
                    onChange={(e) => setStatusFilter(e.target.value)}
                  >
                    <MenuItem value="all">All Statuses</MenuItem>
                    <MenuItem value="pending">Pending</MenuItem>
                    <MenuItem value="processed">Processed</MenuItem>
                    <MenuItem value="failed">Failed</MenuItem>
                  </Select>
                </FormControl>

                <FormControl size="small" sx={{ minWidth: 180 }}>
                  <InputLabel>Payment Method</InputLabel>
                  <Select
                    value={paymentMethodFilter}
                    label="Payment Method"
                    onChange={(e) => setPaymentMethodFilter(e.target.value)}
                  >
                    <MenuItem value="all">All Methods</MenuItem>
                    <MenuItem value="card">Card</MenuItem>
                    <MenuItem value="upi">UPI</MenuItem>
                    <MenuItem value="netbanking">Net Banking</MenuItem>
                    <MenuItem value="wallet">Wallet</MenuItem>
                  </Select>
                </FormControl>

                <Stack direction="row" spacing={1} alignItems="center">
                  <DatePicker
                    label="Start Date"
                    value={startDate}
                    onChange={setStartDate}
                    slots={{
                      textField: (params) => <TextField {...params} size="small" sx={{ width: 150 }} />,
                      openPickerIcon: DateRange
                    }}
                  />
                  <Typography>to</Typography>
                  <DatePicker
                    label="End Date"
                    value={endDate}
                    onChange={setEndDate}
                    slots={{
                      textField: (params) => <TextField {...params} size="small" sx={{ width: 150 }} />,
                      openPickerIcon: DateRange
                    }}
                  />
                </Stack>

                <Box flexGrow={1} />

                <Button
                  variant="contained"
                  startIcon={<Download />}
                  onClick={handleExport}
                  sx={{ ml: 'auto' }}
                >
                  Export
                </Button>
              </Stack>

              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                      <TableCell>Settlement ID</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Order ID</TableCell>
                      <TableCell align="right">Amount (₹)</TableCell>
                      <TableCell align="right">Fees (₹)</TableCell>
                      <TableCell align="right">Tax (₹)</TableCell>
                      <TableCell align="right">Net Amount (₹)</TableCell>
                      <TableCell>Payment Method</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {paginatedSettlements.map((settlement) => (
                      <TableRow key={settlement.id}>
                        <TableCell>{settlement.id.slice(0, 8)}...</TableCell>
                        <TableCell>
                          {new Date(settlement.settlementDate).toLocaleDateString()}
                        </TableCell>
                        <TableCell>{settlement.orderId}</TableCell>
                        <TableCell align="right">{settlement.amount.toFixed(2)}</TableCell>
                        <TableCell align="right">{settlement.fees.toFixed(2)}</TableCell>
                        <TableCell align="right">{settlement.tax.toFixed(2)}</TableCell>
                        <TableCell align="right">{settlement.netAmount.toFixed(2)}</TableCell>
                        <TableCell>
                          {settlement.paymentMethod.charAt(0).toUpperCase() + 
                           settlement.paymentMethod.slice(1)}
                        </TableCell>
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

              <TablePagination
                rowsPerPageOptions={[10, 25, 50]}
                component="div"
                count={filteredSettlements.length}
                rowsPerPage={rowsPerPage}
                page={page}
                onPageChange={handleChangePage}
                onRowsPerPageChange={handleChangeRowsPerPage}
              />

              <Divider sx={{ my: 2 }} />

              <Stack direction="row" justifyContent="flex-end" spacing={4}>
                <Box textAlign="right">
                  <Typography variant="subtitle1">Total Amount:</Typography>
                  <Typography variant="subtitle1">Total Fees:</Typography>
                  <Typography variant="subtitle1">Total Tax:</Typography>
                  <Typography variant="subtitle1" fontWeight="bold">Net Settlement:</Typography>
                </Box>
                <Box textAlign="right">
                  <Typography variant="subtitle1">₹{totalAmount.toFixed(2)}</Typography>
                  <Typography variant="subtitle1">₹{totalFees.toFixed(2)}</Typography>
                  <Typography variant="subtitle1">₹{totalTax.toFixed(2)}</Typography>
                  <Typography variant="subtitle1" fontWeight="bold">₹{totalNet.toFixed(2)}</Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Stack>
      </Container>
    </LocalizationProvider>
  );
};

export default Settlements;