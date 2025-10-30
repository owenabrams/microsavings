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
  CircularProgress,
  Typography
} from '@mui/material';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { groupsAPI } from '../services/api';

export default function AddMemberDialog({ open, onClose, groupId }) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    id_number: '',
    date_of_birth: '',
    gender: '',
    occupation: '',
    address: '',
    role: 'MEMBER',
    status: 'ACTIVE'
  });
  const [error, setError] = useState(null);

  const createMutation = useMutation({
    mutationFn: async (data) => {
      const response = await groupsAPI.addMember(groupId, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['group', groupId]);
      queryClient.invalidateQueries(['groups']);
      handleClose();
    },
    onError: (error) => {
      setError(error.response?.data?.message || 'Failed to add member');
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
    if (!formData.first_name || !formData.last_name) {
      setError('First name and last name are required');
      return;
    }
    if (!formData.phone_number && !formData.email) {
      setError('Either phone number or email is required');
      return;
    }
    createMutation.mutate(formData);
  };

  const handleClose = () => {
    setFormData({
      first_name: '',
      last_name: '',
      email: '',
      phone_number: '',
      id_number: '',
      date_of_birth: '',
      gender: '',
      occupation: '',
      address: '',
      role: 'MEMBER',
      status: 'ACTIVE'
    });
    setError(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Add New Member
        <Typography variant="body2" color="text.secondary">
          Add a new member to the group
        </Typography>
      </DialogTitle>
      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={2} sx={{ mt: 0.5 }}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              label="First Name"
              value={formData.first_name}
              onChange={(e) => handleChange('first_name', e.target.value)}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              label="Last Name"
              value={formData.last_name}
              onChange={(e) => handleChange('last_name', e.target.value)}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Phone Number"
              value={formData.phone_number}
              onChange={(e) => handleChange('phone_number', e.target.value)}
              placeholder="+250 XXX XXX XXX"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="ID Number"
              value={formData.id_number}
              onChange={(e) => handleChange('id_number', e.target.value)}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="date"
              label="Date of Birth"
              value={formData.date_of_birth}
              onChange={(e) => handleChange('date_of_birth', e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              select
              label="Gender"
              value={formData.gender}
              onChange={(e) => handleChange('gender', e.target.value)}
            >
              <MenuItem value="">Select Gender</MenuItem>
              <MenuItem value="MALE">Male</MenuItem>
              <MenuItem value="FEMALE">Female</MenuItem>
              <MenuItem value="OTHER">Other</MenuItem>
            </TextField>
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Occupation"
              value={formData.occupation}
              onChange={(e) => handleChange('occupation', e.target.value)}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Address"
              value={formData.address}
              onChange={(e) => handleChange('address', e.target.value)}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              select
              label="Role"
              value={formData.role}
              onChange={(e) => handleChange('role', e.target.value)}
            >
              <MenuItem value="MEMBER">Member</MenuItem>
              <MenuItem value="CHAIRMAN">Chairman</MenuItem>
              <MenuItem value="VICE_CHAIRMAN">Vice Chairman</MenuItem>
              <MenuItem value="TREASURER">Treasurer</MenuItem>
              <MenuItem value="SECRETARY">Secretary</MenuItem>
              <MenuItem value="OFFICER">Officer</MenuItem>
              <MenuItem value="FOUNDER">Founder</MenuItem>
            </TextField>
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              select
              label="Status"
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
            >
              <MenuItem value="ACTIVE">Active</MenuItem>
              <MenuItem value="INACTIVE">Inactive</MenuItem>
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
          {createMutation.isPending ? 'Adding...' : 'Add Member'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

