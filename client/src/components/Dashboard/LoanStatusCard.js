import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Button,
  LinearProgress,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

function LoanStatusCard({ loans, currency = 'UGX', memberId }) {
  const navigate = useNavigate();
  const {
    is_eligible,
    max_loan_amount,
    overall_score,
    risk_level,
    active_loans_count,
    total_loan_amount,
    total_outstanding,
  } = loans;

  const formatCurrency = (amount) => {
    if (amount >= 1000000) {
      return `${(amount / 1000000).toFixed(1)}M`;
    } else if (amount >= 1000) {
      return `${(amount / 1000).toFixed(1)}K`;
    }
    return amount.toLocaleString();
  };

  const getRiskColor = (risk) => {
    switch (risk?.toUpperCase()) {
      case 'LOW':
        return 'success';
      case 'MEDIUM':
        return 'warning';
      case 'HIGH':
        return 'error';
      default:
        return 'default';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'success.main';
    if (score >= 60) return 'info.main';
    if (score >= 40) return 'warning.main';
    return 'error.main';
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              backgroundColor: is_eligible ? 'success.main' : 'grey.400',
              borderRadius: '50%',
              p: 1,
              display: 'flex',
              mr: 2,
            }}
          >
            <AccountBalanceIcon sx={{ color: 'white', fontSize: 28 }} />
          </Box>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" component="div">
              Loan Status
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Eligibility & Active Loans
            </Typography>
          </Box>
        </Box>

        {/* Eligibility Status */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            {is_eligible ? (
              <CheckCircleIcon sx={{ color: 'success.main', mr: 1 }} />
            ) : (
              <CancelIcon sx={{ color: 'error.main', mr: 1 }} />
            )}
            <Typography variant="body1" fontWeight="medium">
              {is_eligible ? 'Eligible for Loan' : 'Not Eligible'}
            </Typography>
          </Box>

          {is_eligible ? (
            <Alert severity="success" sx={{ mb: 2 }}>
              You can borrow up to <strong>{formatCurrency(max_loan_amount)} {currency}</strong>
            </Alert>
          ) : (
            <Alert severity="info" sx={{ mb: 2 }}>
              Continue saving and attending meetings to become eligible
            </Alert>
          )}
        </Box>

        {/* Loan Score */}
        {overall_score > 0 && (
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="body2" color="text.secondary">
                Loan Score
              </Typography>
              <Typography variant="body2" fontWeight="bold" color={getScoreColor(overall_score)}>
                {overall_score.toFixed(0)}/100
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={overall_score}
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: 'grey.200',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: getScoreColor(overall_score),
                },
              }}
            />
          </Box>
        )}

        {/* Risk Level */}
        {risk_level && risk_level !== 'UNKNOWN' && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
              Risk Level
            </Typography>
            <Chip
              label={risk_level}
              color={getRiskColor(risk_level)}
              size="small"
              sx={{ fontWeight: 'medium' }}
            />
          </Box>
        )}

        {/* Active Loans Summary */}
        <Box
          sx={{
            backgroundColor: 'grey.50',
            borderRadius: 2,
            p: 2,
            mb: 2,
          }}
        >
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Active Loans
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2">Number of Loans:</Typography>
            <Typography variant="body2" fontWeight="medium">
              {active_loans_count}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2">Total Borrowed:</Typography>
            <Typography variant="body2" fontWeight="medium">
              {formatCurrency(total_loan_amount)} {currency}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="body2">Outstanding:</Typography>
            <Typography variant="body2" fontWeight="bold" color="error.main">
              {formatCurrency(total_outstanding)} {currency}
            </Typography>
          </Box>
        </Box>

        {/* Action Button */}
        <Button
          variant="contained"
          fullWidth
          endIcon={<ArrowForwardIcon />}
          onClick={() => navigate(`/loans?memberId=${memberId}`)}
          disabled={!is_eligible}
        >
          {is_eligible ? 'Apply for Loan' : 'View Requirements'}
        </Button>
      </CardContent>
    </Card>
  );
}

export default LoanStatusCard;

