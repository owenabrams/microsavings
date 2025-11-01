import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  MenuItem,
  Alert,
  CircularProgress
} from '@mui/material';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { groupsAPI } from '../services/api';

export default function CreateGroupDialog({ open, onClose }) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    country: 'Rwanda',
    region: '',
    district: '',
    parish: '',
    village: '',
    max_members: 30,
    currency: 'UGX',
    share_value: 1000,
    meeting_frequency: 'WEEKLY',
    meeting_day: 'MONDAY'
  });
  const [error, setError] = useState(null);

  const createMutation = useMutation({
    mutationFn: async (data) => {
      const response = await groupsAPI.create(data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['groups']);
      handleClose();
    },
    onError: (error) => {
      setError(error.response?.data?.message || 'Failed to create group');
    }
  });

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    setError(null);
  };

  const handleSubmit = () => {
    if (!formData.name || !formData.village) {
      setError('Group name and village are required');
      return;
    }
    createMutation.mutate(formData);
  };

  const handleClose = () => {
    setFormData({
      name: '',
      description: '',
      country: 'Rwanda',
      region: '',
      district: '',
      parish: '',
      village: '',
      max_members: 30,
      currency: 'UGX',
      share_value: 1000,
      meeting_frequency: 'WEEKLY',
      meeting_day: 'MONDAY'
    });
    setError(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Create New Savings Group</DialogTitle>
      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={2} sx={{ mt: 0.5 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              required
              label="Group Name"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder="e.g., Kigali Women Savings Group"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Description"
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              placeholder="Brief description of the group's purpose and goals"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              select
              label="Country"
              value={formData.country}
              onChange={(e) => handleChange('country', e.target.value)}
            >
              <MenuItem value="Rwanda">Rwanda</MenuItem>
              <MenuItem value="Uganda">Uganda</MenuItem>
              <MenuItem value="Kenya">Kenya</MenuItem>
              <MenuItem value="Tanzania">Tanzania</MenuItem>
              <MenuItem value="Burundi">Burundi</MenuItem>
            </TextField>
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Region/Province"
              value={formData.region}
              onChange={(e) => handleChange('region', e.target.value)}
              placeholder="e.g., Kigali City"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="District"
              value={formData.district}
              onChange={(e) => handleChange('district', e.target.value)}
              placeholder="e.g., Gasabo"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Parish/Sector"
              value={formData.parish}
              onChange={(e) => handleChange('parish', e.target.value)}
              placeholder="e.g., Remera"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              label="Village/Cell"
              value={formData.village}
              onChange={(e) => handleChange('village', e.target.value)}
              placeholder="e.g., Rukiri I"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="number"
              label="Maximum Members"
              value={formData.max_members}
              onChange={(e) => handleChange('max_members', parseInt(e.target.value))}
              inputProps={{ min: 5, max: 100 }}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              select
              label="Currency"
              value={formData.currency}
              onChange={(e) => handleChange('currency', e.target.value)}
            >
              <MenuItem value="RWF">RWF (Rwandan Franc)</MenuItem>
              <MenuItem value="UGX">UGX (Ugandan Shilling)</MenuItem>
              <MenuItem value="KES">KES (Kenyan Shilling)</MenuItem>
              <MenuItem value="TZS">TZS (Tanzanian Shilling)</MenuItem>
              <MenuItem value="BIF">BIF (Burundian Franc)</MenuItem>
              <MenuItem value="USD">USD (US Dollar)</MenuItem>
            </TextField>
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="number"
              label="Share Value"
              value={formData.share_value}
              onChange={(e) => handleChange('share_value', parseFloat(e.target.value))}
              inputProps={{ min: 0, step: 100 }}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              select
              label="Meeting Frequency"
              value={formData.meeting_frequency}
              onChange={(e) => handleChange('meeting_frequency', e.target.value)}
            >
              <MenuItem value="WEEKLY">Weekly</MenuItem>
              <MenuItem value="BIWEEKLY">Bi-weekly</MenuItem>
              <MenuItem value="MONTHLY">Monthly</MenuItem>
            </TextField>
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              select
              label="Meeting Day"
              value={formData.meeting_day}
              onChange={(e) => handleChange('meeting_day', e.target.value)}
            >
              <MenuItem value="MONDAY">Monday</MenuItem>
              <MenuItem value="TUESDAY">Tuesday</MenuItem>
              <MenuItem value="WEDNESDAY">Wednesday</MenuItem>
              <MenuItem value="THURSDAY">Thursday</MenuItem>
              <MenuItem value="FRIDAY">Friday</MenuItem>
              <MenuItem value="SATURDAY">Saturday</MenuItem>
              <MenuItem value="SUNDAY">Sunday</MenuItem>
            </TextField>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={createMutation.isPending}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={createMutation.isPending}
          startIcon={createMutation.isPending && <CircularProgress size={20} />}
        >
          {createMutation.isPending ? 'Creating...' : 'Create Group'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

