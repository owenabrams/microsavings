import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import { groupsAPI } from '../services/api';

function GroupsList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['groups'],
    queryFn: async () => {
      const response = await groupsAPI.getAll();
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load groups: {error.message}
      </Alert>
    );
  }

  const groups = data?.data?.groups || [];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Savings Groups
        </Typography>
        <Button variant="contained" disabled>
          Create Group
        </Button>
      </Box>

      {groups.length === 0 ? (
        <Alert severity="info">
          No savings groups found. Create your first group to get started.
        </Alert>
      ) : (
        <Grid container spacing={3}>
          {groups.map((group) => (
            <Grid item xs={12} md={6} lg={4} key={group.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {group.name}
                  </Typography>
                  
                  <Chip
                    label={group.status || 'ACTIVE'}
                    color={group.status === 'ACTIVE' ? 'success' : 'default'}
                    size="small"
                    sx={{ mb: 2 }}
                  />

                  {group.description && (
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {group.description}
                    </Typography>
                  )}

                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2">
                      <strong>Location:</strong> {group.village}, {group.parish}
                    </Typography>
                    <Typography variant="body2">
                      <strong>District:</strong> {group.district}{group.region ? `, ${group.region}` : ''}{group.country ? `, ${group.country}` : ''}
                    </Typography>
                    {group.meeting_location && (
                      <Typography variant="body2">
                        <strong>Meeting:</strong> {group.meeting_location}
                      </Typography>
                    )}
                    <Typography variant="body2">
                      <strong>Members:</strong> {group.total_members || 0}{group.max_members ? ` / ${group.max_members}` : ''}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Total Savings:</strong> {group.currency || 'RWF'} {parseFloat(group.total_savings || 0).toLocaleString()}
                    </Typography>
                    {group.share_value && (
                      <Typography variant="body2">
                        <strong>Share Value:</strong> {group.currency || 'RWF'} {parseFloat(group.share_value || 0).toLocaleString()}
                      </Typography>
                    )}
                  </Box>

                  <Button
                    component={Link}
                    to={`/groups/${group.id}`}
                    variant="outlined"
                    fullWidth
                    sx={{ mt: 2 }}
                  >
                    View Details
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <Box sx={{ mt: 3 }}>
        <Typography variant="body2" color="text.secondary">
          Total Groups: {groups.length}
        </Typography>
      </Box>
    </Box>
  );
}

export default GroupsList;

