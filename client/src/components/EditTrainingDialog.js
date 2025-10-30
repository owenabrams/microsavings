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

const EditTrainingDialog = ({ open, onClose, training }) => {
  const [formData, setFormData] = useState({
    training_topic: '',
    training_description: '',
    trainer_name: '',
    duration_minutes: '',
    notes: '',
  });
  const [error, setError] = useState('');
  
  const queryClient = useQueryClient();

  // Initialize form data when training changes
  useEffect(() => {
    if (training) {
      setFormData({
        training_topic: training.training_topic || '',
        training_description: training.training_description || '',
        trainer_name: training.trainer_name || '',
        duration_minutes: training.duration_minutes || '',
        notes: training.notes || '',
      });
    }
  }, [training]);

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data) => transactionsAPI.updateTraining(training.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['meeting']);
      onClose();
    },
    onError: (error) => {
      setError(error.response?.data?.message || 'Failed to update training session');
    },
  });

  const handleSubmit = () => {
    setError('');

    // Validation
    if (!formData.training_topic) {
      setError('Please enter a training topic');
      return;
    }
    if (!formData.duration_minutes || parseInt(formData.duration_minutes) <= 0) {
      setError('Please enter a valid duration');
      return;
    }

    updateMutation.mutate({
      training_topic: formData.training_topic,
      training_description: formData.training_description,
      trainer_name: formData.trainer_name,
      duration_minutes: parseInt(formData.duration_minutes),
      notes: formData.notes,
    });
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError('');
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Edit Training Session
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
          {/* Training Topic */}
          <TextField
            label="Training Topic"
            value={formData.training_topic}
            onChange={(e) => handleChange('training_topic', e.target.value)}
            fullWidth
            required
          />

          {/* Training Description */}
          <TextField
            label="Training Description"
            value={formData.training_description}
            onChange={(e) => handleChange('training_description', e.target.value)}
            fullWidth
            multiline
            rows={3}
            placeholder="Describe the training content"
          />

          {/* Trainer Name */}
          <TextField
            label="Trainer Name"
            value={formData.trainer_name}
            onChange={(e) => handleChange('trainer_name', e.target.value)}
            fullWidth
          />

          {/* Duration */}
          <TextField
            label="Duration (minutes)"
            type="number"
            value={formData.duration_minutes}
            onChange={(e) => handleChange('duration_minutes', e.target.value)}
            fullWidth
            inputProps={{ min: 1, step: 5 }}
            required
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

          {/* Info */}
          <Alert severity="info">
            <Typography variant="body2">
              <strong>Note:</strong> Editing the training session details will not affect attendance records. 
              To modify attendance, please contact an administrator.
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

export default EditTrainingDialog;

