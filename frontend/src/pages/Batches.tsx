import { Button, Card, CardContent, Typography } from '@mui/material';
import { useMutation, useQuery } from 'react-query';
import { generateBatches, getTodayBatches } from '../api/batches';

export default function Batches() {
  const { data: batches, refetch } = useQuery('todayBatches', getTodayBatches);
  const { mutate, isLoading } = useMutation(generateBatches, {
    onSuccess: () => refetch()
  });

  return (
    <div className="p-6">
      <Button 
        variant="contained" 
        onClick={() => mutate()}
        disabled={isLoading}
      >
        {isLoading ? 'Generating...' : 'Generate Batches'}
      </Button>

      <div className="mt-6 space-y-4">
        {batches?.map(batch => (
          <Card key={batch.id}>
            <CardContent>
              <Typography variant="h6">Batch {batch.id.slice(0, 8)}</Typography>
              <Typography>Orders: {batch.orderCount}</Typography>
              <Typography>Weight: {batch.totalWeight} kg</Typography>
              <DriverAssignment batchId={batch.id} />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}