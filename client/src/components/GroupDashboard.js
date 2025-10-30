import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  LinearProgress,
  Chip,
  IconButton,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import SavingsIcon from '@mui/icons-material/Savings';
import PeopleIcon from '@mui/icons-material/People';
import GavelIcon from '@mui/icons-material/Gavel';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import EventIcon from '@mui/icons-material/Event';
import SchoolIcon from '@mui/icons-material/School';
import HowToVoteIcon from '@mui/icons-material/HowToVote';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import { groupsAPI } from '../services/api';

const GroupDashboard = () => {
  const { groupId } = useParams();
  const navigate = useNavigate();

  const { data, isLoading, error } = useQuery({
    queryKey: ['groupDashboard', groupId],
    queryFn: async () => {
      const response = await groupsAPI.getGroupDashboard(groupId);
      return response.data.data;
    },
  });

  const formatCurrency = (amount, currency = 'UGX') => {
    return new Intl.NumberFormat('en-US', {
      style: 'decimal',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount) + ` ${currency}`;
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">Error loading group dashboard: {error.message}</Alert>
      </Box>
    );
  }

  const { group_info, financial_summary, targets, meeting_statistics, participation_statistics } = data;
  const currency = group_info.currency || 'UGX';

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <IconButton onClick={() => navigate(`/groups/${groupId}`)} sx={{ mr: 2 }}>
          <ArrowBackIcon />
        </IconButton>
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h4" gutterBottom>
            {group_info.name} - Group Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Total Members: {group_info.total_members} | Formation Date: {group_info.formation_date ? new Date(group_info.formation_date).toLocaleDateString() : 'N/A'}
          </Typography>
        </Box>
      </Box>

      {/* Targets Progress */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <TrendingUpIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Savings Target Progress</Typography>
          </Box>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Typography variant="body2" color="text.secondary">Group Target</Typography>
              <Typography variant="h6">{formatCurrency(targets.group_target, currency)}</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="body2" color="text.secondary">Current Savings</Typography>
              <Typography variant="h6">{formatCurrency(targets.current_savings, currency)}</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="body2" color="text.secondary">Progress</Typography>
              <Typography variant="h6">{targets.progress_percentage.toFixed(1)}%</Typography>
            </Grid>
          </Grid>
          <Box sx={{ mt: 2 }}>
            <LinearProgress 
              variant="determinate" 
              value={Math.min(targets.progress_percentage, 100)} 
              sx={{ height: 10, borderRadius: 5 }}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Financial Summary */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <SavingsIcon sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="h6">Total Savings</Typography>
              </Box>
              <Typography variant="h4">{formatCurrency(financial_summary.total_savings, currency)}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <GavelIcon sx={{ mr: 1, color: 'warning.main' }} />
                <Typography variant="h6">Total Fines</Typography>
              </Box>
              <Typography variant="h5">{formatCurrency(financial_summary.total_fines_issued, currency)}</Typography>
              <Typography variant="body2" color="text.secondary">
                Paid: {formatCurrency(financial_summary.total_fines_paid, currency)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <AccountBalanceIcon sx={{ mr: 1, color: 'info.main' }} />
                <Typography variant="h6">Loans</Typography>
              </Box>
              <Typography variant="h5">{formatCurrency(financial_summary.total_loans_disbursed, currency)}</Typography>
              <Typography variant="body2" color="text.secondary">
                Outstanding: {formatCurrency(financial_summary.total_loans_outstanding, currency)}
              </Typography>
              <Chip 
                label={`${financial_summary.active_loans_count} Active Loans`} 
                size="small" 
                color="info" 
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <EventIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Meetings</Typography>
              </Box>
              <Typography variant="h5">{meeting_statistics.completed_meetings}</Typography>
              <Typography variant="body2" color="text.secondary">
                Total: {meeting_statistics.total_meetings}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Avg Attendance: {meeting_statistics.average_attendance_rate.toFixed(1)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Savings by Fund Type */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Savings by Fund Type</Typography>
          <Grid container spacing={2}>
            {Object.entries(financial_summary.savings_by_fund).map(([fundName, fundData]) => (
              <Grid item xs={12} sm={6} md={4} key={fundName}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>{fundName}</Typography>
                    <Typography variant="h6" color="primary">
                      {formatCurrency(fundData.total, currency)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Deposits: {formatCurrency(fundData.deposits, currency)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Withdrawals: {formatCurrency(fundData.withdrawals, currency)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
          {Object.keys(financial_summary.savings_by_fund).length === 0 && (
            <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
              No savings recorded yet
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* Participation Statistics */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SchoolIcon sx={{ mr: 1, color: 'secondary.main' }} />
                <Typography variant="h6">Training Participation</Typography>
              </Box>
              <Typography variant="h4" color="secondary">
                {participation_statistics.training_participation_rate.toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Total Trainings: {participation_statistics.total_trainings}
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={participation_statistics.training_participation_rate} 
                color="secondary"
                sx={{ mt: 2, height: 8, borderRadius: 4 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <HowToVoteIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Voting Participation</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {participation_statistics.voting_participation_rate.toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Total Voting Sessions: {participation_statistics.total_voting_sessions}
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={participation_statistics.voting_participation_rate} 
                sx={{ mt: 2, height: 8, borderRadius: 4 }}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default GroupDashboard;

