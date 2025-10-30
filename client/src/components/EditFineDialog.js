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

const EditFineDialog = ({ open, onClose, fine, currency = 'UGX' }) => {
  const [formData, setFormData] = useState({
    fine_type: '',
    amount: '',
    reason: '',
    notes: '',
  });
  const [error, setError] = useState('');
  
  const queryClient = useQueryClient();

  // Initialize form data when fine changes
  useEffect(() => {
    if (fine) {
      setFormData({
        fine_type: fine.fine_type || '',
        amount: fine.amount || '',
        reason: fine.reason || '',
        notes: fine.notes || '',
      });
    }
  }, [fine]);

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data) => transactionsAPI.updateFine(fine.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['meeting']);
      onClose();
    },
    onError: (error) => {
      setError(error.response?.data?.message || 'Failed to update fine');
    },
  });

  const handleSubmit = () => {
    setError('');

    // Validation
    if (!formData.fine_type) {
      setError('Please select a fine type');
      return;
    }
    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      setError('Please enter a valid amount');
      return;
    }

    updateMutation.mutate({
      fine_type: formData.fine_type,
      amount: parseFloat(formData.amount),
      reason: formData.reason,
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
        Edit Fine
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
            value={fine?.member_name || ''}
            disabled
            fullWidth
          />

          {/* Fine Type */}
          <FormControl fullWidth>
            <InputLabel>Fine Type</InputLabel>
            <Select
              value={formData.fine_type}
              onChange={(e) => handleChange('fine_type', e.target.value)}
              label="Fine Type"
            >
              <MenuItem value="LATE_ARRIVAL">Late Arrival</MenuItem>
              <MenuItem value="ABSENCE">Absence</MenuItem>
              <MenuItem value="MISSED_CONTRIBUTION">Missed Contribution</MenuItem>
              <MenuItem value="RULE_VIOLATION">Rule Violation</MenuItem>
              <MenuItem value="OTHER">Other</MenuItem>
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

          {/* Reason */}
          <TextField
            label="Reason"
            value={formData.reason}
            onChange={(e) => handleChange('reason', e.target.value)}
            fullWidth
            multiline
            rows={2}
            placeholder="Reason for the fine"
          />

          {/* Notes */}
          <TextField
            label="Notes"
            value={formData.notes}
            onChange={(e) => handleChange('notes', e.target.value)}
            fullWidth
            multiline
            rows={2}
            placeholder="Optional notes or corrections"
          />

          {/* Warning */}
          <Alert severity="warning">
            <Typography variant="body2">
              <strong>Warning:</strong> Editing this fine will affect member balances and group totals. 
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

export default EditFineDialog;

