import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Divider,
} from '@mui/material';
import SavingsIcon from '@mui/icons-material/Savings';
import ChildCareIcon from '@mui/icons-material/ChildCare';
import GroupsIcon from '@mui/icons-material/Groups';

function SavingsByFundCard({ savings, currency = 'UGX' }) {
  const { by_fund, total } = savings;

  const formatCurrency = (amount) => {
    if (amount >= 1000000) {
      return `${(amount / 1000000).toFixed(1)}M`;
    } else if (amount >= 1000) {
      return `${(amount / 1000).toFixed(1)}K`;
    }
    return amount.toLocaleString();
  };

  const getFundIcon = (fundName) => {
    if (fundName.toLowerCase().includes('personal')) {
      return <SavingsIcon sx={{ color: 'primary.main' }} />;
    } else if (fundName.toLowerCase().includes('ecd')) {
      return <ChildCareIcon sx={{ color: 'secondary.main' }} />;
    } else if (fundName.toLowerCase().includes('social')) {
      return <GroupsIcon sx={{ color: 'success.main' }} />;
    }
    return <SavingsIcon sx={{ color: 'info.main' }} />;
  };

  const getFundColor = (fundName) => {
    if (fundName.toLowerCase().includes('personal')) return 'primary';
    if (fundName.toLowerCase().includes('ecd')) return 'secondary';
    if (fundName.toLowerCase().includes('social')) return 'success';
    return 'info';
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Savings by Fund
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Total: {formatCurrency(total)} {currency}
          </Typography>
        </Box>

        {by_fund.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body2" color="text.secondary">
              No savings data available
            </Typography>
          </Box>
        ) : (
          <Box>
            {by_fund.map((fund, index) => {
              const percentage = total > 0 ? (fund.balance / total) * 100 : 0;
              
              return (
                <Box key={fund.name}>
                  {index > 0 && <Divider sx={{ my: 2 }} />}
                  
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
                    <Box sx={{ mr: 1.5, mt: 0.5 }}>
                      {getFundIcon(fund.name)}
                    </Box>
                    <Box sx={{ flexGrow: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="body1" fontWeight="medium">
                          {fund.name}
                        </Typography>
                        <Typography variant="body1" fontWeight="bold" color={`${getFundColor(fund.name)}.main`}>
                          {formatCurrency(fund.balance)} {currency}
                        </Typography>
                      </Box>
                      
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                        {fund.description}
                      </Typography>

                      <LinearProgress
                        variant="determinate"
                        value={percentage}
                        color={getFundColor(fund.name)}
                        sx={{ height: 6, borderRadius: 3, mb: 1 }}
                      />

                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="caption" color="text.secondary">
                          Deposits: {formatCurrency(fund.total_deposits)} {currency}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {percentage.toFixed(1)}% of total
                        </Typography>
                      </Box>

                      {fund.total_withdrawals > 0 && (
                        <Typography variant="caption" color="text.secondary">
                          Withdrawals: {formatCurrency(fund.total_withdrawals)} {currency}
                        </Typography>
                      )}
                    </Box>
                  </Box>
                </Box>
              );
            })}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

export default SavingsByFundCard;

