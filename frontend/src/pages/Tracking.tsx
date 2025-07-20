import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Container,
  Divider,
  IconButton,
  Paper,
  Stack,
  Stepper,
  Step,
  StepLabel,
  Typography
} from '@mui/material';
import {
  Refresh,
  Directions,
  Phone,
  Chat,
  LocationOn,
  CheckCircle,
  LocalShipping,
  Restaurant,
  Assignment
} from '@mui/icons-material';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { fetchTrackingDetails } from '../api/tracking';
import Map from '../components/LiveMap';
import EstimatedTimeArrival from '../components/EstimatedTimeArrival';

const statusSteps = [
  'Order Received',
  'Preparing',
  'Picked Up',
  'On the Way',
  'Delivered'
];

const Tracking = () => {
  const { orderId } = useParams();
  const [lastUpdated, setLastUpdated] = useState(new Date().toLocaleTimeString());
  const [isMapLoaded, setIsMapLoaded] = useState(false);

  const { data: trackingData, isLoading, isError, refetch } = useQuery({
    queryKey: ['tracking', orderId],
    queryFn: () => fetchTrackingDetails(orderId ?? ""),
    refetchInterval: 30000, // Auto-refresh every 30 seconds
  });

  useEffect(() => {
    if (trackingData) {
      setLastUpdated(new Date().toLocaleTimeString());
    }
  }, [trackingData]);

  const activeStep = () => {
    switch (trackingData?.currentStatus) {
      case 'preparing': return 1;
      case 'picked_up': return 2;
      case 'on_the_way': return 3;
      case 'delivered': return 4;
      default: return 0;
    }
  };

  const handleRefresh = () => {
    refetch();
  };

  const handleCallDriver = () => {
    window.location.href = `tel:${trackingData?.driverPhone}`;
  };

  const handleOpenDirections = () => {
    if (trackingData?.driverLocation) {
      const url = `https://www.google.com/maps/dir/?api=1&destination=${trackingData.deliveryLocation.lat},${trackingData.deliveryLocation.lng}`;
      window.open(url, '_blank');
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (isError || !trackingData) {
    return (
      <Box textAlign="center" p={4}>
        <Typography color="error" gutterBottom>
          Failed to load tracking information
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={handleRefresh}
        >
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Container maxWidth="lg">
      <Stack spacing={3} sx={{ my: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h4" component="h1">
            Order Tracking
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Last updated: {lastUpdated}
          </Typography>
        </Stack>

        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 3 }}>
          <Box sx={{ flex: '1 1 66%' }}>
            <Card elevation={3}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  <Assignment sx={{ mr: 1 }} /> Order #{trackingData.orderId}
                </Typography>
                <Divider sx={{ my: 2 }} />

                <Box sx={{ width: '100%', mb: 4 }}>
                  <Stepper activeStep={activeStep()} alternativeLabel>
                    {statusSteps.map((label) => (
                      <Step key={label}>
                        <StepLabel>{label}</StepLabel>
                      </Step>
                    ))}
                  </Stepper>
                </Box>

                <Box sx={{ height: 400, position: 'relative' }}>
                  {!isMapLoaded && (
                    <Box
                      display="flex"
                      justifyContent="center"
                      alignItems="center"
                      height="100%"
                    >
                      <CircularProgress />
                    </Box>
                  )}
                  <Map
                    driverLocation={trackingData.driverLocation}
                    stops={[
                      trackingData.restaurantLocation,
                      trackingData.deliveryLocation
                    ]}
                  />
                </Box>
              </CardContent>
            </Card>
          </Box>

          <Box sx={{ flex: '1 1 33%' }}>
            <Stack spacing={3}>
              <Card elevation={3}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <LocalShipping sx={{ mr: 1 }} /> Delivery Information
                  </Typography>
                  <Divider sx={{ my: 2 }} />

                  <Stack spacing={2}>
                    <Box>
                      <Typography variant="subtitle2" color="text.secondary">
                        Estimated Delivery Time
                      </Typography>
                      <EstimatedTimeArrival 
                        eta={trackingData.estimatedDeliveryTime} 
                        status={trackingData.currentStatus}
                      />
                    </Box>

                    <Box>
                      <Typography variant="subtitle2" color="text.secondary">
                        Delivery To
                      </Typography>
                      <Typography>
                        {trackingData.customerName}
                      </Typography>
                      <Typography variant="body2" sx={{ display: 'flex', alignItems: 'center' }}>
                        <LocationOn fontSize="small" sx={{ mr: 0.5 }} />
                        {trackingData.deliveryAddress}
                      </Typography>
                    </Box>

                    <Box>
                      <Typography variant="subtitle2" color="text.secondary">
                        Restaurant
                      </Typography>
                      <Typography sx={{ display: 'flex', alignItems: 'center' }}>
                        <Restaurant fontSize="small" sx={{ mr: 0.5 }} />
                        {trackingData.restaurantName}
                      </Typography>
                    </Box>
                  </Stack>
                </CardContent>
              </Card>

              <Card elevation={3}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <LocalShipping sx={{ mr: 1 }} /> Driver Details
                  </Typography>
                  <Divider sx={{ my: 2 }} />

                  <Stack spacing={2}>
                    <Typography variant="subtitle1">
                      {trackingData.driverName}
                    </Typography>

                    <Stack direction="row" spacing={2}>
                      <Button
                        variant="contained"
                        startIcon={<Phone />}
                        fullWidth
                        onClick={handleCallDriver}
                      >
                        Call Driver
                      </Button>
                      <Button
                        variant="outlined"
                        startIcon={<Directions />}
                        fullWidth
                        onClick={handleOpenDirections}
                      >
                        Directions
                      </Button>
                    </Stack>

                    <Button
                      variant="text"
                      startIcon={<Chat />}
                      fullWidth
                      sx={{ mt: 1 }}
                    >
                      Message Driver
                    </Button>
                  </Stack>
                </CardContent>
              </Card>

              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={handleRefresh}
                fullWidth
              >
                Refresh Status
              </Button>
            </Stack>
          </Box>
        </Box>

        <Card elevation={3}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Tracking History
            </Typography>
            <Divider sx={{ my: 2 }} />

            <Stack spacing={2}>
              {trackingData.steps.map((step, index) => (
                <Box key={index} sx={{ display: 'flex', alignItems: 'flex-start' }}>
                  <Box sx={{ mr: 2, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <CheckCircle color="primary" />
                    {index < trackingData.steps.length - 1 && (
                      <Divider orientation="vertical" sx={{ flexGrow: 1, my: 1 }} />
                    )}
                  </Box>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="subtitle1">{step.status}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {new Date(step.timestamp).toLocaleString()}
                    </Typography>
                    {step.description && (
                      <Typography variant="body2" sx={{ mt: 0.5 }}>
                        {step.description}
                      </Typography>
                    )}
                  </Box>
                </Box>
              ))}
            </Stack>
          </CardContent>
        </Card>
      </Stack>
    </Container>
  );
};

export default Tracking;