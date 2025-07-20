import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Container,
  Divider,
  Grid,
  IconButton,
  Paper,
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
  Add,
  Delete,
  Edit,
  Refresh,
  Search,
  Visibility
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { 
  fetchDrivers, 
  deleteDriver 
} from '../api/drivers';
import ConfirmationDialog from '../components/ConfirmationDialog';

interface Driver {
  id: string;
  name: string;
  email: string;
  phone: string;
  licenseNumber: string;
  vehicleType: string;
  status: 'active' | 'inactive' | 'on_leave';
  createdAt: string;
}

const Drivers: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedDriver, setSelectedDriver] = useState<Driver | null>(null);

  const { data: drivers, isLoading, isError, refetch } = useQuery<Driver[]>({
    queryKey: ['drivers'],
    queryFn: fetchDrivers
  });

  const deleteMutation = useMutation({
    mutationFn: deleteDriver,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['drivers'] });
      setDeleteDialogOpen(false);
    }
  });

  const handleDelete = (driver: Driver) => {
    setSelectedDriver(driver);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = () => {
    if (selectedDriver) {
      deleteMutation.mutate(selectedDriver.id);
    }
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const filteredDrivers = drivers?.filter(driver =>
    driver.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    driver.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    driver.phone.includes(searchTerm)
  ) || [];

  const paginatedDrivers = filteredDrivers.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

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
          Failed to load drivers
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
    <Container maxWidth="lg">
      <Stack spacing={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Driver Management
        </Typography>

        <Card>
          <CardContent>
            <Stack 
              direction="row" 
              justifyContent="space-between" 
              alignItems="center"
              spacing={2}
              mb={3}
            >
              <TextField
                variant="outlined"
                size="small"
                placeholder="Search drivers..."
                InputProps={{
                  startAdornment: <Search color="action" sx={{ mr: 1 }} />
                }}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                sx={{ width: 300 }}
              />
              <Button
                variant="contained"
                startIcon={<Add />}
                component={Link}
                to="/drivers/new"
              >
                Add Driver
              </Button>
            </Stack>

            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                    <TableCell>Name</TableCell>
                    <TableCell>Contact</TableCell>
                    <TableCell>License</TableCell>
                    <TableCell>Vehicle</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {paginatedDrivers.map((driver) => (
                    <TableRow key={driver.id}>
                      <TableCell>
                        <Typography fontWeight="medium">{driver.name}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          Joined: {new Date(driver.createdAt).toLocaleDateString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography>{driver.email}</Typography>
                        <Typography variant="body2">{driver.phone}</Typography>
                      </TableCell>
                      <TableCell>{driver.licenseNumber}</TableCell>
                      <TableCell>{driver.vehicleType}</TableCell>
                      <TableCell>
                        <Box
                          component="span"
                          sx={{
                            px: 1,
                            py: 0.5,
                            borderRadius: 1,
                            backgroundColor:
                              driver.status === 'active' ? '#e8f5e9' :
                              driver.status === 'on_leave' ? '#fff8e1' : '#ffebee',
                            color:
                              driver.status === 'active' ? '#2e7d32' :
                              driver.status === 'on_leave' ? '#f57f17' : '#c62828',
                          }}
                        >
                          {driver.status.replace('_', ' ')}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={1}>
                          <IconButton
                            size="small"
                            onClick={() => navigate(`/drivers/${driver.id}`)}
                          >
                            <Visibility fontSize="small" />
                          </IconButton>
                          <IconButton
                            size="small"
                            onClick={() => navigate(`/drivers/${driver.id}/edit`)}
                          >
                            <Edit fontSize="small" />
                          </IconButton>
                          <IconButton
                            size="small"
                            onClick={() => handleDelete(driver)}
                            color="error"
                          >
                            <Delete fontSize="small" />
                          </IconButton>
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            <TablePagination
              rowsPerPageOptions={[5, 10, 25]}
              component="div"
              count={filteredDrivers.length}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
            />
          </CardContent>
        </Card>
      </Stack>

      <ConfirmationDialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        onConfirm={handleConfirmDelete}
        title="Confirm Delete"
        content={`Are you sure you want to delete driver ${selectedDriver?.name}?`}
        loading={deleteMutation.isPending}
      />
    </Container>
  );
};

export default Drivers;