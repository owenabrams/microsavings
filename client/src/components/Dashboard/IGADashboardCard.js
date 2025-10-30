import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Grid,
  Chip,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import BusinessCenterIcon from '@mui/icons-material/BusinessCenter';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import InfoIcon from '@mui/icons-material/Info';

function IGADashboardCard({ iga, memberId }) {
  const navigate = useNavigate();
  const {
    active_campaigns,
    total_invested,
    total_returns,
    roi_percentage,
  } = iga;

  const formatCurrency = (amount) => {
    if (amount >= 1000000) {
      return `${(amount / 1000000).toFixed(1)}M`;
    } else if (amount >= 1000) {
      return `${(amount / 1000).toFixed(1)}K`;
    }
    return amount.toLocaleString();
  };

  const hasIGAActivity = active_campaigns > 0 || total_invested > 0;
  const isPositiveROI = roi_percentage > 0;

  const getROIColor = () => {
    if (roi_percentage >= 20) return 'success.main';
    if (roi_percentage >= 10) return 'info.main';
    if (roi_percentage > 0) return 'warning.main';
    return 'text.secondary';
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              backgroundColor: hasIGAActivity ? 'primary.main' : 'grey.400',
              borderRadius: '50%',
              p: 1,
              display: 'flex',
              mr: 2,
            }}
          >
            <BusinessCenterIcon sx={{ color: 'white', fontSize: 28 }} />
          </Box>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" component="div">
              IGA Participation
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Income Generating Activities
            </Typography>
          </Box>
          {hasIGAActivity && (
            <Chip
              label="Active"
              color="success"
              size="small"
            />
          )}
        </Box>

        {!hasIGAActivity ? (
          <Box>
            <Alert severity="info" icon={<InfoIcon />} sx={{ mb: 2 }}>
              You haven't participated in any IGA campaigns yet. Join a campaign to start earning!
            </Alert>

            <Box
              sx={{
                backgroundColor: 'grey.50',
                borderRadius: 2,
                p: 2,
                textAlign: 'center',
                mb: 2,
              }}
            >
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                IGA campaigns help members generate additional income through group investments
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Examples: Poultry farming, Tailoring, Small retail businesses
              </Typography>
            </Box>
          </Box>
        ) : (
          <Box>
            {/* ROI Highlight */}
            <Box
              sx={{
                backgroundColor: isPositiveROI ? 'success.50' : 'grey.50',
                borderRadius: 2,
                p: 2,
                mb: 2,
                textAlign: 'center',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                <TrendingUpIcon sx={{ color: getROIColor(), mr: 1 }} />
                <Typography variant="body2" color="text.secondary">
                  Return on Investment
                </Typography>
              </Box>
              <Typography variant="h3" fontWeight="bold" color={getROIColor()}>
                {roi_percentage.toFixed(1)}%
              </Typography>
            </Box>

            {/* IGA Metrics */}
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={4}>
                <Box
                  sx={{
                    backgroundColor: 'grey.50',
                    borderRadius: 2,
                    p: 1.5,
                    textAlign: 'center',
                  }}
                >
                  <Typography variant="caption" color="text.secondary">
                    Active Campaigns
                  </Typography>
                  <Typography variant="h5" fontWeight="bold" color="primary.main">
                    {active_campaigns}
                  </Typography>
                </Box>
              </Grid>

              <Grid item xs={4}>
                <Box
                  sx={{
                    backgroundColor: 'grey.50',
                    borderRadius: 2,
                    p: 1.5,
                    textAlign: 'center',
                  }}
                >
                  <Typography variant="caption" color="text.secondary">
                    Invested
                  </Typography>
                  <Typography variant="body1" fontWeight="bold" color="info.main">
                    {formatCurrency(total_invested)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    RWF
                  </Typography>
                </Box>
              </Grid>

              <Grid item xs={4}>
                <Box
                  sx={{
                    backgroundColor: 'grey.50',
                    borderRadius: 2,
                    p: 1.5,
                    textAlign: 'center',
                  }}
                >
                  <Typography variant="caption" color="text.secondary">
                    Returns
                  </Typography>
                  <Typography variant="body1" fontWeight="bold" color="success.main">
                    {formatCurrency(total_returns)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    RWF
                  </Typography>
                </Box>
              </Grid>
            </Grid>

            {/* Net Profit */}
            <Box
              sx={{
                backgroundColor: 'primary.50',
                borderRadius: 2,
                p: 1.5,
                mb: 2,
              }}
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  Net Profit
                </Typography>
                <Typography variant="h6" fontWeight="bold" color="primary.main">
                  {formatCurrency(total_returns - total_invested)} RWF
                </Typography>
              </Box>
            </Box>
          </Box>
        )}

        {/* Action Button */}
        <Button
          variant="contained"
          fullWidth
          endIcon={<ArrowForwardIcon />}
          onClick={() => navigate(`/campaigns?memberId=${memberId}`)}
        >
          {hasIGAActivity ? 'View My Campaigns' : 'Browse Campaigns'}
        </Button>
      </CardContent>
    </Card>
  );
}

export default IGADashboardCard;

