import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Alert,
  CircularProgress,
  IconButton,
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { transactionsAPI } from '../services/api';

const EditLoanRepaymentDialog = ({ open, onClose, repayment, currency = 'UGX' }) => {
  const [formData, setFormData] = useState({
    principal_amount: '',
    interest_amount: '',
    notes: '',
  });
  const [error, setError] = useState('');
  
  const queryClient = useQueryClient();

  // Initialize form data when repayment changes
  useEffect(() => {
    if (repayment) {
      setFormData({
        principal_amount: repayment.principal_amount || '',
        interest_amount: repayment.interest_amount || '',
        notes: repayment.notes || '',
      });
    }
  }, [repayment]);

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data) => {
      if (!repayment || !repayment.id) {
        throw new Error('Repayment not found');
      }
      return transactionsAPI.updateLoanRepayment(repayment.id, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['meeting']);
      onClose();
    },
    onError: (error) => {
      setError(error.response?.data?.message || 'Failed to update loan repayment');
    },
  });

  const handleSubmit = () => {
    setError('');

    // Validation
    const principal = parseFloat(formData.principal_amount) || 0;
    const interest = parseFloat(formData.interest_amount) || 0;

    if (principal <= 0 && interest <= 0) {
      setError('Please enter at least one amount (principal or interest)');
      return;
    }

    updateMutation.mutate({
      principal_amount: principal,
      interest_amount: interest,
      notes: formData.notes,
    });
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError('');
  };

  const totalAmount = (parseFloat(formData.principal_amount) || 0) + (parseFloat(formData.interest_amount) || 0);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        Edit Loan Repayment
        <IconButton
          onClick={onClose}
          sx={{ position: 'absolute', right: 8, top: 8 }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          {/* Member Info (Read-only) */}
          <TextField
            label="Member"
            value={repayment?.member_name || ''}
            disabled
            fullWidth
          />

          {/* Principal Amount */}
          <TextField
            label={`Principal Amount (${currency})`}
            type="number"
            value={formData.principal_amount}
            onChange={(e) => handleChange('principal_amount', e.target.value)}
            fullWidth
            inputProps={{ min: 0, step: 100 }}
          />

          {/* Interest Amount */}
          <TextField
            label={`Interest Amount (${currency})`}
            type="number"
            value={formData.interest_amount}
            onChange={(e) => handleChange('interest_amount', e.target.value)}
            fullWidth
            inputProps={{ min: 0, step: 100 }}
          />

          {/* Total Amount Display */}
          <Alert severity="info">
            <Typography variant="body2">
              <strong>Total Repayment:</strong> {currency} {totalAmount.toLocaleString()}
            </Typography>
          </Alert>

          {/* Notes */}
          <TextField
            label="Notes"
            value={formData.notes}
            onChange={(e) => handleChange('notes', e.target.value)}
            fullWidth
            multiline
            rows={3}
            placeholder="Optional notes or corrections"
          />

          {/* Warning */}
          <Alert severity="warning">
            <Typography variant="body2">
              <strong>Warning:</strong> Editing this repayment will affect loan balances and group totals. 
              Make sure the correction is accurate.
            </Typography>
          </Alert>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={updateMutation.isPending}>
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={updateMutation.isPending}
          startIcon={updateMutation.isPending ? <CircularProgress size={20} /> : null}
        >
          {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EditLoanRepaymentDialog;

