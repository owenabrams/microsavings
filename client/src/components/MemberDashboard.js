import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  Button,
  Breadcrumbs,
  Link,
} from '@mui/material';
import { membersAPI } from '../services/api';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import HomeIcon from '@mui/icons-material/Home';
import SavingsProgressCard from './Dashboard/SavingsProgressCard';
import SavingsByFundCard from './Dashboard/SavingsByFundCard';
import LoanStatusCard from './Dashboard/LoanStatusCard';
import PerformanceComparisonCard from './Dashboard/PerformanceComparisonCard';
import FinancialMetricsCard from './Dashboard/FinancialMetricsCard';
import IGADashboardCard from './Dashboard/IGADashboardCard';

function MemberDashboard() {
  const { memberId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, [memberId]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await membersAPI.getDashboard(memberId);
      
      if (response.data.status === 'success') {
        setDashboardData(response.data.data);
      } else {
        setError(response.data.message || 'Failed to load dashboard data');
      }
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err.response?.data?.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button
          variant="contained"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate(-1)}
        >
          Go Back
        </Button>
      </Box>
    );
  }

  if (!dashboardData) {
    return (
      <Alert severity="warning">No dashboard data available</Alert>
    );
  }

  const { member, group, savings, loans, performance, fines, iga } = dashboardData;

  return (
    <Box>
      {/* Breadcrumbs */}
      <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 3 }}>
        <Link
          underline="hover"
          sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}
          color="inherit"
          onClick={() => navigate('/dashboard')}
        >
          <HomeIcon sx={{ mr: 0.5 }} fontSize="inherit" />
          Dashboard
        </Link>
        <Link
          underline="hover"
          color="inherit"
          sx={{ cursor: 'pointer' }}
          onClick={() => navigate('/groups')}
        >
          Groups
        </Link>
        <Link
          underline="hover"
          color="inherit"
          sx={{ cursor: 'pointer' }}
          onClick={() => navigate(`/groups/${group.id}`)}
        >
          {group.name}
        </Link>
        <Typography color="text.primary">
          {member.first_name} {member.last_name}
        </Typography>
      </Breadcrumbs>

      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          {member.first_name} {member.last_name}'s Financial Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {group.name} • {member.role} • Joined {new Date(member.joined_date).toLocaleDateString()}
        </Typography>
      </Box>

      {/* Dashboard Cards Grid */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <SavingsProgressCard savings={savings} />
        </Grid>

        <Grid item xs={12} md={6}>
          <SavingsByFundCard savings={savings} />
        </Grid>

        <Grid item xs={12} md={6}>
          <LoanStatusCard loans={loans} memberId={memberId} />
        </Grid>

        <Grid item xs={12} md={6}>
          <PerformanceComparisonCard performance={performance} />
        </Grid>

        <Grid item xs={12} md={6}>
          <FinancialMetricsCard performance={performance} fines={fines} />
        </Grid>

        <Grid item xs={12} md={6}>
          <IGADashboardCard iga={iga} memberId={memberId} />
        </Grid>
      </Grid>

      {/* Back Button */}
      <Box sx={{ mt: 4 }}>
        <Button
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate(`/groups/${group.id}`)}
        >
          Back to Group
        </Button>
      </Box>
    </Box>
  );
}

export default MemberDashboard;

