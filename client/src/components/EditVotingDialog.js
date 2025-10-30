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

const EditVotingDialog = ({ open, onClose, voting }) => {
  const [formData, setFormData] = useState({
    vote_topic: '',
    vote_description: '',
    notes: '',
  });
  const [error, setError] = useState('');
  
  const queryClient = useQueryClient();

  // Initialize form data when voting changes
  useEffect(() => {
    if (voting) {
      setFormData({
        vote_topic: voting.vote_topic || '',
        vote_description: voting.vote_description || '',
        notes: voting.notes || '',
      });
    }
  }, [voting]);

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data) => transactionsAPI.updateVoting(voting.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['meeting']);
      onClose();
    },
    onError: (error) => {
      setError(error.response?.data?.message || 'Failed to update voting session');
    },
  });

  const handleSubmit = () => {
    setError('');

    // Validation
    if (!formData.vote_topic) {
      setError('Please enter a voting topic');
      return;
    }

    updateMutation.mutate({
      vote_topic: formData.vote_topic,
      vote_description: formData.vote_description,
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
        Edit Voting Session
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
          {/* Vote Topic */}
          <TextField
            label="Voting Topic"
            value={formData.vote_topic}
            onChange={(e) => handleChange('vote_topic', e.target.value)}
            fullWidth
            required
          />

          {/* Vote Description */}
          <TextField
            label="Voting Description"
            value={formData.vote_description}
            onChange={(e) => handleChange('vote_description', e.target.value)}
            fullWidth
            multiline
            rows={4}
            placeholder="Describe what is being voted on"
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

          {/* Voting Results Display (Read-only) */}
          {voting && (
            <Alert severity="info">
              <Typography variant="body2">
                <strong>Current Results:</strong><br />
                Yes: {voting.yes_votes || 0} | 
                No: {voting.no_votes || 0} | 
                Abstain: {voting.abstain_votes || 0}
              </Typography>
              <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                To modify vote results, please contact an administrator.
              </Typography>
            </Alert>
          )}

          {/* Info */}
          <Alert severity="info">
            <Typography variant="body2">
              <strong>Note:</strong> Editing the voting session details will not affect individual vote records. 
              To modify votes, please contact an administrator.
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

export default EditVotingDialog;

