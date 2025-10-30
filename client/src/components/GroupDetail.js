import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { groupsAPI } from '../services/api';

function GroupDetail() {
  const { groupId } = useParams();
  const navigate = useNavigate();

  const { data, isLoading, error } = useQuery({
    queryKey: ['group', groupId],
    queryFn: async () => {
      const response = await groupsAPI.getById(groupId);
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
      <Box>
        <Button component={Link} to="/groups" startIcon={<ArrowBackIcon />} sx={{ mb: 2 }}>
          Back to Groups
        </Button>
        <Alert severity="error">
          Failed to load group details: {error.message}
        </Alert>
      </Box>
    );
  }

  const group = data?.data || {};
  const members = group.members || [];
  const financialSummary = group.financial_summary || {};

  return (
    <Box>
      <Button component={Link} to="/groups" startIcon={<ArrowBackIcon />} sx={{ mb: 2 }}>
        Back to Groups
      </Button>

      <Typography variant="h4" component="h1" gutterBottom>
        {group.name}
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Group Information
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Status
                  </Typography>
                  <Chip
                    label={group.status || 'ACTIVE'}
                    color={group.status === 'ACTIVE' ? 'success' : 'default'}
                    size="small"
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Total Members
                  </Typography>
                  <Typography variant="body1">
                    {members.length}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    Location
                  </Typography>
                  <Typography variant="body1">
                    {group.village}, {group.parish}, {group.district}, {group.country}
                  </Typography>
                </Grid>
                {group.description && (
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                      Description
                    </Typography>
                    <Typography variant="body1">
                      {group.description}
                    </Typography>
                  </Grid>
                )}
              </Grid>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Members
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Role</TableCell>
                      <TableCell>Phone</TableCell>
                      <TableCell align="right">Contributions</TableCell>
                      <TableCell align="right">Attendance</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {members.map((member) => (
                      <TableRow
                        key={member.id}
                        hover
                        sx={{ cursor: 'pointer' }}
                        onClick={() => navigate(`/dashboard/member/${member.id}`)}
                      >
                        <TableCell>
                          <Typography
                            color="primary"
                            sx={{ fontWeight: 500, '&:hover': { textDecoration: 'underline' } }}
                          >
                            {member.first_name} {member.last_name}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip label={member.role} size="small" />
                        </TableCell>
                        <TableCell>{member.phone_number}</TableCell>
                        <TableCell align="right">
                          RWF {parseFloat(member.total_contributions || 0).toLocaleString()}
                        </TableCell>
                        <TableCell align="right">
                          {parseFloat(member.attendance_percentage || 0).toFixed(1)}%
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Financial Summary
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Total Savings
                </Typography>
                <Typography variant="h5" color="success.main">
                  RWF {parseFloat(financialSummary.total_savings || 0).toLocaleString()}
                </Typography>
              </Box>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Total Loans
                </Typography>
                <Typography variant="h6">
                  RWF {parseFloat(financialSummary.total_loans || 0).toLocaleString()}
                </Typography>
              </Box>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Average Attendance
                </Typography>
                <Typography variant="h6">
                  {parseFloat(financialSummary.average_attendance || 0).toFixed(1)}%
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default GroupDetail;

