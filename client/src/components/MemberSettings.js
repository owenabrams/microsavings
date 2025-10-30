import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button,
  Tabs, Tab, Box, TextField, Grid, MenuItem, FormControlLabel,
  Switch, CircularProgress, Alert, Typography, Divider
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import CloseIcon from '@mui/icons-material/Close';
import api from '../services/api';

function TabPanel({ children, value, index }) {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ py: 2 }}>{children}</Box>}
    </div>
  );
}

function MemberSettings({ open, onClose, groupId, memberId }) {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState(0);
  const [formData, setFormData] = useState(null);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState(null);

  // Fetch member profile
  const { data: profileData, isLoading: profileLoading } = useQuery({
    queryKey: ['memberProfile', groupId, memberId],
    queryFn: async () => {
      const response = await api.get(`/api/groups/${groupId}/members/${memberId}/profile`);
      return response.data.data;
    },
    enabled: open
  });

  // Fetch member settings
  const { data: settingsData, isLoading: settingsLoading } = useQuery({
    queryKey: ['memberSettings', groupId, memberId],
    queryFn: async () => {
      const response = await api.get(`/api/groups/${groupId}/members/${memberId}/settings`);
      return response.data.data;
    },
    enabled: open
  });

  // Initialize form data when data is loaded
  useEffect(() => {
    if (profileData && settingsData && !formData) {
      setFormData({
        // Personal Info
        first_name: profileData.first_name || '',
        last_name: profileData.last_name || '',
        email: profileData.email || '',
        phone_number: profileData.phone_number || '',
        id_number: profileData.id_number || '',
        date_of_birth: profileData.date_of_birth ? profileData.date_of_birth.split('T')[0] : '',
        gender: profileData.gender || '',
        occupation: profileData.occupation || '',
        address: profileData.address || '',
        emergency_contact_name: profileData.emergency_contact_name || '',
        emergency_contact_phone: profileData.emergency_contact_phone || '',
        notes: profileData.notes || '',
        
        // Membership Details
        status: settingsData.status || 'ACTIVE',
        role: settingsData.role || 'MEMBER',
        joined_date: settingsData.joined_date ? settingsData.joined_date.split('T')[0] : '',
        is_active: settingsData.is_active !== false,
        
        // Permissions
        can_view_finances: settingsData.can_view_finances !== false,
        can_apply_for_loans: settingsData.can_apply_for_loans !== false,
        can_vote: settingsData.can_vote !== false,
        
        // Notification Preferences
        notification_preferences: settingsData.notification_preferences || {
          email: true,
          sms: true,
          push: true
        }
      });
    }
  }, [profileData, settingsData, formData]);

  // Update profile mutation
  const updateProfileMutation = useMutation({
    mutationFn: async (data) => {
      return await api.put(`/api/groups/${groupId}/members/${memberId}/profile`, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['memberProfile', groupId, memberId]);
      setSaveSuccess(true);
      setSaveError(null);
      setTimeout(() => setSaveSuccess(false), 3000);
    },
    onError: (error) => {
      setSaveError(error.response?.data?.message || 'Failed to update profile');
      setSaveSuccess(false);
    }
  });

  // Update settings mutation
  const updateSettingsMutation = useMutation({
    mutationFn: async (data) => {
      return await api.put(`/api/groups/${groupId}/members/${memberId}/settings`, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['memberSettings', groupId, memberId]);
      setSaveSuccess(true);
      setSaveError(null);
      setTimeout(() => setSaveSuccess(false), 3000);
    },
    onError: (error) => {
      setSaveError(error.response?.data?.message || 'Failed to update settings');
      setSaveSuccess(false);
    }
  });

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleNotificationChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      notification_preferences: {
        ...prev.notification_preferences,
        [field]: value
      }
    }));
  };

  const handleSave = async () => {
    if (!formData) return;

    try {
      // Save personal info
      const profileFields = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email,
        phone_number: formData.phone_number,
        id_number: formData.id_number,
        date_of_birth: formData.date_of_birth,
        gender: formData.gender,
        occupation: formData.occupation,
        address: formData.address,
        emergency_contact_name: formData.emergency_contact_name,
        emergency_contact_phone: formData.emergency_contact_phone,
        notes: formData.notes
      };
      await updateProfileMutation.mutateAsync(profileFields);

      // Save settings
      const settingsFields = {
        status: formData.status,
        role: formData.role,
        is_active: formData.is_active,
        can_view_finances: formData.can_view_finances,
        can_apply_for_loans: formData.can_apply_for_loans,
        can_vote: formData.can_vote,
        notification_preferences: formData.notification_preferences
      };
      await updateSettingsMutation.mutateAsync(settingsFields);

    } catch (error) {
      console.error('Error saving member settings:', error);
    }
  };

  const handleClose = () => {
    setFormData(null);
    setActiveTab(0);
    setSaveSuccess(false);
    setSaveError(null);
    onClose();
  };

  const isLoading = profileLoading || settingsLoading;
  const isSaving = updateProfileMutation.isPending || updateSettingsMutation.isPending;

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Member Settings
        {isLoading && <CircularProgress size={20} sx={{ ml: 2 }} />}
      </DialogTitle>

      <DialogContent dividers>
        {saveSuccess && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Member settings updated successfully!
          </Alert>
        )}
        {saveError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {saveError}
          </Alert>
        )}

        {isLoading ? (
          <Box display="flex" justifyContent="center" p={4}>
            <CircularProgress />
          </Box>
        ) : formData ? (
          <>
            <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tab label="Personal Info" />
              <Tab label="Membership" />
              <Tab label="Permissions" />
            </Tabs>

            {/* Personal Info Tab */}
            <TabPanel value={activeTab} index={0}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="First Name"
                    value={formData.first_name}
                    onChange={(e) => handleChange('first_name', e.target.value)}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Last Name"
                    value={formData.last_name}
                    onChange={(e) => handleChange('last_name', e.target.value)}
                    required
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
                    label="Date of Birth"
                    type="date"
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
                    <MenuItem value="M">Male</MenuItem>
                    <MenuItem value="F">Female</MenuItem>
                    <MenuItem value="Other">Other</MenuItem>
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
                    label="Address"
                    multiline
                    rows={2}
                    value={formData.address}
                    onChange={(e) => handleChange('address', e.target.value)}
                  />
                </Grid>

                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle2" gutterBottom>Emergency Contact</Typography>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Emergency Contact Name"
                    value={formData.emergency_contact_name}
                    onChange={(e) => handleChange('emergency_contact_name', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Emergency Contact Phone"
                    value={formData.emergency_contact_phone}
                    onChange={(e) => handleChange('emergency_contact_phone', e.target.value)}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Notes"
                    multiline
                    rows={3}
                    value={formData.notes}
                    onChange={(e) => handleChange('notes', e.target.value)}
                    helperText="Internal notes about this member"
                  />
                </Grid>
              </Grid>
            </TabPanel>

            {/* Membership Tab */}
            <TabPanel value={activeTab} index={1}>
              <Grid container spacing={2}>
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
                    <MenuItem value="SUSPENDED">Suspended</MenuItem>
                  </TextField>
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
                    label="Joined Date"
                    type="date"
                    value={formData.joined_date}
                    onChange={(e) => handleChange('joined_date', e.target.value)}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.is_active}
                        onChange={(e) => handleChange('is_active', e.target.checked)}
                      />
                    }
                    label="Active Member"
                  />
                </Grid>
              </Grid>
            </TabPanel>

            {/* Permissions Tab */}
            <TabPanel value={activeTab} index={2}>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>Member Permissions</Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.can_view_finances}
                        onChange={(e) => handleChange('can_view_finances', e.target.checked)}
                      />
                    }
                    label="Can View Group Finances"
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.can_apply_for_loans}
                        onChange={(e) => handleChange('can_apply_for_loans', e.target.checked)}
                      />
                    }
                    label="Can Apply for Loans"
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.can_vote}
                        onChange={(e) => handleChange('can_vote', e.target.checked)}
                      />
                    }
                    label="Can Participate in Voting"
                  />
                </Grid>

                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle2" gutterBottom>Notification Preferences</Typography>
                </Grid>

                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.notification_preferences?.email}
                        onChange={(e) => handleNotificationChange('email', e.target.checked)}
                      />
                    }
                    label="Email Notifications"
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.notification_preferences?.sms}
                        onChange={(e) => handleNotificationChange('sms', e.target.checked)}
                      />
                    }
                    label="SMS Notifications"
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.notification_preferences?.push}
                        onChange={(e) => handleNotificationChange('push', e.target.checked)}
                      />
                    }
                    label="Push Notifications"
                  />
                </Grid>
              </Grid>
            </TabPanel>
          </>
        ) : null}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} startIcon={<CloseIcon />} disabled={isSaving}>
          Cancel
        </Button>
        <Button
          onClick={handleSave}
          variant="contained"
          startIcon={<SaveIcon />}
          disabled={isSaving || !formData}
        >
          {isSaving ? 'Saving...' : 'Save Changes'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default MemberSettings;

