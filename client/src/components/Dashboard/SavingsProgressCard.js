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
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';

function SavingsProgressCard({ savings, currency = 'UGX' }) {
  const { total, target, progress_percentage } = savings;

  const formatCurrency = (amount) => {
    if (amount >= 1000000) {
      return `${(amount / 1000000).toFixed(1)}M`;
    } else if (amount >= 1000) {
      return `${(amount / 1000).toFixed(1)}K`;
    }
    return amount.toLocaleString();
  };

  const getProgressColor = () => {
    if (progress_percentage >= 100) return 'success';
    if (progress_percentage >= 75) return 'primary';
    if (progress_percentage >= 50) return 'info';
    if (progress_percentage >= 25) return 'warning';
    return 'error';
  };

  const isOnTrack = progress_percentage >= 50;

  return (
    <Card sx={{ height: '100%', position: 'relative', overflow: 'visible' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              backgroundColor: 'primary.main',
              borderRadius: '50%',
              p: 1,
              display: 'flex',
              mr: 2,
            }}
          >
            <AccountBalanceWalletIcon sx={{ color: 'white', fontSize: 28 }} />
          </Box>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" component="div">
              Total Savings
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Your accumulated savings
            </Typography>
          </Box>
          <Chip
            icon={isOnTrack ? <TrendingUpIcon /> : <TrendingDownIcon />}
            label={isOnTrack ? 'On Track' : 'Below Target'}
            color={isOnTrack ? 'success' : 'warning'}
            size="small"
          />
        </Box>

        <Typography variant="h3" color="primary" sx={{ fontWeight: 'bold', mb: 1 }}>
          {formatCurrency(total)} {currency}
        </Typography>

        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="body2" color="text.secondary">
              Progress to Target
            </Typography>
            <Typography variant="body2" fontWeight="medium">
              {progress_percentage.toFixed(1)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={Math.min(progress_percentage, 100)}
            color={getProgressColor()}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>

        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            pt: 2,
            borderTop: '1px solid',
            borderColor: 'divider',
          }}
        >
          <Box>
            <Typography variant="caption" color="text.secondary">
              Current
            </Typography>
            <Typography variant="body1" fontWeight="medium">
              {total.toLocaleString()} {currency}
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'right' }}>
            <Typography variant="caption" color="text.secondary">
              Target
            </Typography>
            <Typography variant="body1" fontWeight="medium">
              {target > 0 ? `${target.toLocaleString()} ${currency}` : 'Not Set'}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

export default SavingsProgressCard;

