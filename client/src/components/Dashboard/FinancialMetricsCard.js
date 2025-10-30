import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  Divider,
} from '@mui/material';
import EventAvailableIcon from '@mui/icons-material/EventAvailable';
import SchoolIcon from '@mui/icons-material/School';
import GavelIcon from '@mui/icons-material/Gavel';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';

function FinancialMetricsCard({ performance, fines, currency = 'UGX' }) {
  const {
    attendance_rate,
    total_meetings,
    attended_meetings,
  } = performance;

  const {
    total: total_fines,
    paid: paid_fines,
    outstanding: outstanding_fines,
  } = fines;

  const formatCurrency = (amount) => {
    if (amount >= 1000000) {
      return `${(amount / 1000000).toFixed(1)}M`;
    } else if (amount >= 1000) {
      return `${(amount / 1000).toFixed(1)}K`;
    }
    return amount.toLocaleString();
  };

  const getAttendanceStatus = () => {
    if (attendance_rate >= 90) return { label: 'Excellent', color: 'success' };
    if (attendance_rate >= 75) return { label: 'Good', color: 'info' };
    if (attendance_rate >= 60) return { label: 'Fair', color: 'warning' };
    return { label: 'Poor', color: 'error' };
  };

  const attendanceStatus = getAttendanceStatus();
  const hasFines = total_fines > 0;
  const hasOutstandingFines = outstanding_fines > 0;

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="h6" component="div" sx={{ mb: 3 }}>
          Financial Metrics
        </Typography>

        {/* Attendance Section */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Box
              sx={{
                backgroundColor: `${attendanceStatus.color}.main`,
                borderRadius: '50%',
                p: 1,
                display: 'flex',
                mr: 2,
              }}
            >
              <EventAvailableIcon sx={{ color: 'white', fontSize: 24 }} />
            </Box>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Meeting Attendance
              </Typography>
              <Typography variant="h5" fontWeight="bold">
                {attendance_rate.toFixed(1)}%
              </Typography>
            </Box>
            <Chip
              label={attendanceStatus.label}
              color={attendanceStatus.color}
              size="small"
            />
          </Box>

          <Box
            sx={{
              backgroundColor: 'grey.50',
              borderRadius: 2,
              p: 1.5,
            }}
          >
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="caption" color="text.secondary">
                  Attended
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {attended_meetings}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="caption" color="text.secondary">
                  Total Meetings
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  {total_meetings}
                </Typography>
              </Grid>
            </Grid>
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Training Section - Placeholder for Phase 1 completion */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Box
              sx={{
                backgroundColor: 'info.main',
                borderRadius: '50%',
                p: 1,
                display: 'flex',
                mr: 2,
              }}
            >
              <SchoolIcon sx={{ color: 'white', fontSize: 24 }} />
            </Box>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Training Participation
              </Typography>
              <Typography variant="body1" fontWeight="medium">
                Coming Soon
              </Typography>
            </Box>
          </Box>
          <Typography variant="caption" color="text.secondary">
            Training tracking will be available in the next update
          </Typography>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Fines Section */}
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Box
              sx={{
                backgroundColor: hasOutstandingFines ? 'error.main' : 'success.main',
                borderRadius: '50%',
                p: 1,
                display: 'flex',
                mr: 2,
              }}
            >
              <GavelIcon sx={{ color: 'white', fontSize: 24 }} />
            </Box>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Fines Status
              </Typography>
              <Typography variant="h6" fontWeight="bold">
                {formatCurrency(total_fines)} {currency}
              </Typography>
            </Box>
            {!hasFines ? (
              <CheckCircleIcon sx={{ color: 'success.main', fontSize: 28 }} />
            ) : hasOutstandingFines ? (
              <WarningIcon sx={{ color: 'error.main', fontSize: 28 }} />
            ) : (
              <CheckCircleIcon sx={{ color: 'success.main', fontSize: 28 }} />
            )}
          </Box>

          <Box
            sx={{
              backgroundColor: hasOutstandingFines ? 'error.50' : 'grey.50',
              borderRadius: 2,
              p: 1.5,
            }}
          >
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <Typography variant="caption" color="text.secondary">
                  Total
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {formatCurrency(total_fines)}
                </Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography variant="caption" color="text.secondary">
                  Paid
                </Typography>
                <Typography variant="body2" fontWeight="medium" color="success.main">
                  {formatCurrency(paid_fines)}
                </Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography variant="caption" color="text.secondary">
                  Outstanding
                </Typography>
                <Typography variant="body2" fontWeight="bold" color="error.main">
                  {formatCurrency(outstanding_fines)}
                </Typography>
              </Grid>
            </Grid>
          </Box>

          {hasOutstandingFines && (
            <Box sx={{ mt: 1 }}>
              <Chip
                label="Payment Required"
                color="error"
                size="small"
                icon={<WarningIcon />}
              />
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}

export default FinancialMetricsCard;

