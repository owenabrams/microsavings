import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';

function PerformanceComparisonCard({ performance, currency = 'UGX' }) {
  const {
    member_savings,
    group_avg_savings,
    attendance_rate,
    group_avg_attendance,
    total_contributions,
  } = performance;

  const formatCurrency = (amount) => {
    if (amount >= 1000000) {
      return `${(amount / 1000000).toFixed(1)}M`;
    } else if (amount >= 1000) {
      return `${(amount / 1000).toFixed(1)}K`;
    }
    return amount.toLocaleString();
  };

  const savingsDiff = member_savings - group_avg_savings;
  const savingsPercentDiff = group_avg_savings > 0 
    ? ((savingsDiff / group_avg_savings) * 100) 
    : 0;
  const isSavingsAboveAvg = savingsDiff >= 0;

  const attendanceDiff = attendance_rate - group_avg_attendance;
  const isAttendanceAboveAvg = attendanceDiff >= 0;

  const getPerformanceLevel = () => {
    const aboveAvgCount = [isSavingsAboveAvg, isAttendanceAboveAvg].filter(Boolean).length;
    if (aboveAvgCount === 2) return { label: 'Excellent', color: 'success' };
    if (aboveAvgCount === 1) return { label: 'Good', color: 'info' };
    return { label: 'Needs Improvement', color: 'warning' };
  };

  const performanceLevel = getPerformanceLevel();

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              backgroundColor: `${performanceLevel.color}.main`,
              borderRadius: '50%',
              p: 1,
              display: 'flex',
              mr: 2,
            }}
          >
            <EmojiEventsIcon sx={{ color: 'white', fontSize: 28 }} />
          </Box>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" component="div">
              Performance Comparison
            </Typography>
            <Typography variant="caption" color="text.secondary">
              You vs Group Average
            </Typography>
          </Box>
          <Chip
            label={performanceLevel.label}
            color={performanceLevel.color}
            size="small"
          />
        </Box>

        {/* Savings Comparison */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="body2" fontWeight="medium">
              Savings Performance
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              {isSavingsAboveAvg ? (
                <TrendingUpIcon sx={{ color: 'success.main', fontSize: 20, mr: 0.5 }} />
              ) : (
                <TrendingDownIcon sx={{ color: 'error.main', fontSize: 20, mr: 0.5 }} />
              )}
              <Typography
                variant="body2"
                fontWeight="bold"
                color={isSavingsAboveAvg ? 'success.main' : 'error.main'}
              >
                {isSavingsAboveAvg ? '+' : ''}{savingsPercentDiff.toFixed(1)}%
              </Typography>
            </Box>
          </Box>

          <Box sx={{ mb: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="caption" color="text.secondary">
                Your Savings
              </Typography>
              <Typography variant="caption" fontWeight="medium">
                {formatCurrency(member_savings)} {currency}
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={Math.min((member_savings / Math.max(member_savings, group_avg_savings)) * 100, 100)}
              color={isSavingsAboveAvg ? 'success' : 'warning'}
              sx={{ height: 6, borderRadius: 3 }}
            />
          </Box>

          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="caption" color="text.secondary">
                Group Average
              </Typography>
              <Typography variant="caption" fontWeight="medium">
                {formatCurrency(group_avg_savings)} {currency}
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={Math.min((group_avg_savings / Math.max(member_savings, group_avg_savings)) * 100, 100)}
              color="info"
              sx={{ height: 6, borderRadius: 3 }}
            />
          </Box>
        </Box>

        {/* Attendance Comparison */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="body2" fontWeight="medium">
              Attendance Performance
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              {isAttendanceAboveAvg ? (
                <TrendingUpIcon sx={{ color: 'success.main', fontSize: 20, mr: 0.5 }} />
              ) : (
                <TrendingDownIcon sx={{ color: 'error.main', fontSize: 20, mr: 0.5 }} />
              )}
              <Typography
                variant="body2"
                fontWeight="bold"
                color={isAttendanceAboveAvg ? 'success.main' : 'error.main'}
              >
                {isAttendanceAboveAvg ? '+' : ''}{attendanceDiff.toFixed(1)}%
              </Typography>
            </Box>
          </Box>

          <Box sx={{ mb: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="caption" color="text.secondary">
                Your Attendance
              </Typography>
              <Typography variant="caption" fontWeight="medium">
                {attendance_rate.toFixed(1)}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={attendance_rate}
              color={isAttendanceAboveAvg ? 'success' : 'warning'}
              sx={{ height: 6, borderRadius: 3 }}
            />
          </Box>

          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="caption" color="text.secondary">
                Group Average
              </Typography>
              <Typography variant="caption" fontWeight="medium">
                {group_avg_attendance.toFixed(1)}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={group_avg_attendance}
              color="info"
              sx={{ height: 6, borderRadius: 3 }}
            />
          </Box>
        </Box>

        {/* Total Contributions */}
        <Box
          sx={{
            backgroundColor: 'grey.50',
            borderRadius: 2,
            p: 2,
            textAlign: 'center',
          }}
        >
          <Typography variant="caption" color="text.secondary">
            Total Contributions
          </Typography>
          <Typography variant="h5" fontWeight="bold" color="primary.main">
            {formatCurrency(total_contributions)} {currency}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}

export default PerformanceComparisonCard;

