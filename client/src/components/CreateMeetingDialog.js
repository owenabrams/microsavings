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
} from '@mui/material';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { meetingsAPI, groupsAPI } from '../services/api';

export default function CreateMeetingDialog({ open, onClose, groupId }) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    meeting_date: new Date().toISOString().split('T')[0],
    meeting_time: '14:00',
    meeting_type: 'REGULAR',
    location: '',
    agenda: '',
    chairperson_id: '',
    secretary_id: '',
    treasurer_id: '',
  });
  const [error, setError] = useState(null);

  // Fetch group members for role selection
  const { data: membersData } = useQuery({
    queryKey: ['groupMembers', groupId],
    queryFn: async () => {
      const response = await groupsAPI.getMembers(groupId);
      return response.data;
    },
    enabled: open && !!groupId,
  });

  const createMutation = useMutation({
    mutationFn: async (data) => {
      const response = await meetingsAPI.createMeeting(groupId, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['meetings', groupId]);
      handleClose();
    },
    onError: (error) => {
      setError(error.response?.data?.message || 'Failed to create meeting');
    },
  });

  const handleChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
    setError(null);
  };

  const handleSubmit = () => {
    if (!formData.meeting_date) {
      setError('Meeting date is required');
      return;
    }

    // Convert empty strings to null for optional fields
    const submitData = {
      ...formData,
      chairperson_id: formData.chairperson_id || null,
      secretary_id: formData.secretary_id || null,
      treasurer_id: formData.treasurer_id || null,
      location: formData.location || null,
      agenda: formData.agenda || null,
      meeting_time: formData.meeting_time || null,
    };

    createMutation.mutate(submitData);
  };

  const handleClose = () => {
    setFormData({
      meeting_date: new Date().toISOString().split('T')[0],
      meeting_time: '14:00',
      meeting_type: 'REGULAR',
      location: '',
      agenda: '',
      chairperson_id: '',
      secretary_id: '',
      treasurer_id: '',
    });
    setError(null);
    onClose();
  };

  const members = membersData?.data?.members || [];

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Create New Meeting</DialogTitle>
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
              type="date"
              label="Meeting Date"
              value={formData.meeting_date}
              onChange={(e) => handleChange('meeting_date', e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="time"
              label="Meeting Time"
              value={formData.meeting_time}
              onChange={(e) => handleChange('meeting_time', e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              select
              label="Meeting Type"
              value={formData.meeting_type}
              onChange={(e) => handleChange('meeting_type', e.target.value)}
            >
              <MenuItem value="REGULAR">Regular</MenuItem>
              <MenuItem value="EMERGENCY">Emergency</MenuItem>
              <MenuItem value="SPECIAL">Special</MenuItem>
              <MenuItem value="AGM">Annual General Meeting</MenuItem>
            </TextField>
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Location"
              value={formData.location}
              onChange={(e) => handleChange('location', e.target.value)}
              placeholder="Meeting location"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Agenda"
              value={formData.agenda}
              onChange={(e) => handleChange('agenda', e.target.value)}
              placeholder="Meeting agenda and topics to discuss"
            />
          </Grid>

          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              select
              label="Chairperson"
              value={formData.chairperson_id}
              onChange={(e) => handleChange('chairperson_id', e.target.value)}
            >
              <MenuItem value="">
                <em>None</em>
              </MenuItem>
              {members.map((member) => (
                <MenuItem key={member.id} value={member.id}>
                  {member.first_name} {member.last_name} ({member.role})
                </MenuItem>
              ))}
            </TextField>
          </Grid>

          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              select
              label="Secretary"
              value={formData.secretary_id}
              onChange={(e) => handleChange('secretary_id', e.target.value)}
            >
              <MenuItem value="">
                <em>None</em>
              </MenuItem>
              {members.map((member) => (
                <MenuItem key={member.id} value={member.id}>
                  {member.first_name} {member.last_name} ({member.role})
                </MenuItem>
              ))}
            </TextField>
          </Grid>

          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              select
              label="Treasurer"
              value={formData.treasurer_id}
              onChange={(e) => handleChange('treasurer_id', e.target.value)}
            >
              <MenuItem value="">
                <em>None</em>
              </MenuItem>
              {members.map((member) => (
                <MenuItem key={member.id} value={member.id}>
                  {member.first_name} {member.last_name} ({member.role})
                </MenuItem>
              ))}
            </TextField>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={createMutation.isPending}
        >
          {createMutation.isPending ? <CircularProgress size={24} /> : 'Create Meeting'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

