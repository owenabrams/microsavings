import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Typography,
  Alert,
  CircularProgress,
  IconButton,
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { transactionsAPI } from '../services/api';

const EditSavingsTransactionDialog = ({ open, onClose, transaction, savingTypes = [], currency = 'UGX' }) => {
  const [formData, setFormData] = useState({
    saving_type_id: '',
    transaction_type: '',
    amount: '',
    notes: '',
  });
  const [error, setError] = useState('');
  
  const queryClient = useQueryClient();

  // Initialize form data when transaction changes
  useEffect(() => {
    if (transaction) {
      setFormData({
        saving_type_id: transaction.saving_type_id || '',
        transaction_type: transaction.transaction_type || '',
        amount: transaction.amount || '',
        notes: transaction.notes || '',
      });
    }
  }, [transaction]);

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data) => {
      if (!transaction || !transaction.id) {
        throw new Error('Transaction not found');
      }
      return transactionsAPI.updateSavingsTransaction(transaction.id, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['meeting']);
      onClose();
    },
    onError: (error) => {
      setError(error.response?.data?.message || 'Failed to update transaction');
    },
  });

  const handleSubmit = () => {
    setError('');

    // Validation
    if (!formData.saving_type_id) {
      setError('Please select a saving type');
      return;
    }
    if (!formData.transaction_type) {
      setError('Please select a transaction type');
      return;
    }
    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      setError('Please enter a valid amount');
      return;
    }

    updateMutation.mutate({
      saving_type_id: parseInt(formData.saving_type_id),
      transaction_type: formData.transaction_type,
      amount: parseFloat(formData.amount),
      notes: formData.notes,
    });
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError('');
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        Edit Savings Transaction
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
            value={transaction?.member_name || ''}
            disabled
            fullWidth
          />

          {/* Saving Type */}
          <FormControl fullWidth>
            <InputLabel>Saving Type</InputLabel>
            <Select
              value={formData.saving_type_id}
              onChange={(e) => handleChange('saving_type_id', e.target.value)}
              label="Saving Type"
            >
              {savingTypes.map((type) => (
                <MenuItem key={type.id} value={type.id}>
                  {type.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Transaction Type */}
          <FormControl fullWidth>
            <InputLabel>Transaction Type</InputLabel>
            <Select
              value={formData.transaction_type}
              onChange={(e) => handleChange('transaction_type', e.target.value)}
              label="Transaction Type"
            >
              <MenuItem value="DEPOSIT">Deposit</MenuItem>
              <MenuItem value="WITHDRAWAL">Withdrawal</MenuItem>
            </Select>
          </FormControl>

          {/* Amount */}
          <TextField
            label={`Amount (${currency})`}
            type="number"
            value={formData.amount}
            onChange={(e) => handleChange('amount', e.target.value)}
            fullWidth
            inputProps={{ min: 0, step: 100 }}
          />

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
              <strong>Warning:</strong> Editing this transaction will affect member balances and group totals. 
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

export default EditSavingsTransactionDialog;

