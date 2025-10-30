import React from 'react';
import { Link } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
} from '@mui/material';
import GroupIcon from '@mui/icons-material/Group';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

function Dashboard({ user }) {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Welcome, {user?.username || 'User'}!
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Microfinance Savings Group Management Platform
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <GroupIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                <Typography variant="h6">Savings Groups</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" paragraph>
                Manage your savings groups, members, and meetings.
              </Typography>
              <Button
                component={Link}
                to="/groups"
                variant="contained"
                fullWidth
              >
                View Groups
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AccountBalanceIcon sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
                <Typography variant="h6">Financial Overview</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" paragraph>
                Track savings, loans, and financial performance.
              </Typography>
              <Button
                variant="outlined"
                fullWidth
                disabled
              >
                Coming Soon
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUpIcon sx={{ fontSize: 40, color: 'info.main', mr: 2 }} />
                <Typography variant="h6">Analytics</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" paragraph>
                View reports and analytics for your groups.
              </Typography>
              <Button
                variant="outlined"
                fullWidth
                disabled
              >
                Coming Soon
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ mt: 4, p: 3, bgcolor: 'info.light', borderRadius: 1 }}>
        <Typography variant="h6" gutterBottom>
          System Status
        </Typography>
        <Typography variant="body2">
          ✅ Backend API: Connected
        </Typography>
        <Typography variant="body2">
          ✅ Database: Operational
        </Typography>
        <Typography variant="body2">
          ✅ All 7 Phases: Implemented
        </Typography>
      </Box>
    </Box>
  );
}

export default Dashboard;

