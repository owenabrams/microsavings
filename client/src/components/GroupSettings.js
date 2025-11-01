import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  TextField,
  Grid,
  Switch,
  FormControlLabel,
  MenuItem,
  Divider,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import SaveIcon from '@mui/icons-material/Save';
import SettingsIcon from '@mui/icons-material/Settings';
import api from '../services/api';
import ManageSavingTypes from './ManageSavingTypes';
import GroupDocumentsTab from './GroupDocumentsTab';

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index} style={{ paddingTop: '24px' }}>
      {value === index && children}
    </div>
  );
}

function GroupSettings() {
  const { groupId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState(0);
  const [formData, setFormData] = useState(null);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [manageSavingTypesOpen, setManageSavingTypesOpen] = useState(false);

  // Get current user to check admin status
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setCurrentUser(JSON.parse(userData));
    }
  }, []);

  const { data, isLoading, error } = useQuery({
    queryKey: ['groupSettings', groupId],
    queryFn: async () => {
      const response = await api.get(`/api/groups/${groupId}/settings`);
      return response.data;
    },
    retry: 1, // Only retry once on failure
  });

  // Set form data when query succeeds
  useEffect(() => {
    if (data?.data) {
      setFormData(data.data);
    }
  }, [data]);

  const updateMutation = useMutation({
    mutationFn: async (updatedData) => {
      const response = await api.put(
        `/api/groups/${groupId}/settings`,
        updatedData
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['groupSettings', groupId]);
      queryClient.invalidateQueries(['group', groupId]);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    }
  });

  const handleChange = (section, field, value) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const handleSave = () => {
    updateMutation.mutate(formData);
  };

  if (isLoading || !formData) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Button component={Link} to={`/groups/${groupId}`} startIcon={<ArrowBackIcon />} sx={{ mb: 2 }}>
          Back to Group
        </Button>
        <Alert severity="error">
          Failed to load group settings: {error.message}
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Button component={Link} to={`/groups/${groupId}`} startIcon={<ArrowBackIcon />}>
          Back to Group
        </Button>
        <Button 
          variant="contained" 
          startIcon={<SaveIcon />}
          onClick={handleSave}
          disabled={updateMutation.isLoading}
        >
          {updateMutation.isLoading ? 'Saving...' : 'Save Changes'}
        </Button>
      </Box>

      <Typography variant="h4" component="h1" gutterBottom>
        {formData.group_name} - Settings
      </Typography>

      {saveSuccess && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Settings saved successfully!
        </Alert>
      )}

      {updateMutation.isError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Failed to save settings: {updateMutation.error.message}
        </Alert>
      )}

      <Card>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Basic Info" />
          <Tab label="Location & Meeting" />
          <Tab label="Financial Settings" />
          <Tab label="Activities" />
          <Tab label="Loan Settings" />
          <Tab label="Fine Settings" />
          <Tab label="Documents" />
        </Tabs>

        <CardContent>
          {/* Basic Info Tab */}
          <TabPanel value={activeTab} index={0}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Group Name"
                  value={formData.basic_info?.name || ''}
                  onChange={(e) => handleChange('basic_info', 'name', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  select
                  label="Status"
                  value={formData.basic_info?.status || 'ACTIVE'}
                  onChange={(e) => handleChange('basic_info', 'status', e.target.value)}
                >
                  <MenuItem value="ACTIVE">Active</MenuItem>
                  <MenuItem value="INACTIVE">Inactive</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Description"
                  value={formData.basic_info?.description || ''}
                  onChange={(e) => handleChange('basic_info', 'description', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="date"
                  label="Formation Date"
                  value={formData.basic_info?.formation_date ? formData.basic_info.formation_date.split('T')[0] : ''}
                  onChange={(e) => handleChange('basic_info', 'formation_date', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Maximum Members"
                  value={formData.basic_info?.max_members || ''}
                  onChange={(e) => handleChange('basic_info', 'max_members', parseInt(e.target.value))}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Saving Cycle (months)"
                  value={formData.basic_info?.saving_cycle_months || 12}
                  onChange={(e) => handleChange('basic_info', 'saving_cycle_months', parseInt(e.target.value))}
                />
              </Grid>
            </Grid>
          </TabPanel>

          {/* Location & Meeting Tab */}
          <TabPanel value={activeTab} index={1}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Region"
                  value={formData.location?.region || ''}
                  onChange={(e) => handleChange('location', 'region', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="District"
                  value={formData.location?.district || ''}
                  onChange={(e) => handleChange('location', 'district', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Parish"
                  value={formData.location?.parish || ''}
                  onChange={(e) => handleChange('location', 'parish', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Village"
                  value={formData.location?.village || ''}
                  onChange={(e) => handleChange('location', 'village', e.target.value)}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Meeting Location"
                  value={formData.location?.meeting_location || ''}
                  onChange={(e) => handleChange('location', 'meeting_location', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Latitude"
                  value={formData.location?.latitude || ''}
                  onChange={(e) => handleChange('location', 'latitude', parseFloat(e.target.value))}
                  inputProps={{ step: "any" }}
                  helperText="GPS coordinate (e.g., -1.9403)"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Longitude"
                  value={formData.location?.longitude || ''}
                  onChange={(e) => handleChange('location', 'longitude', parseFloat(e.target.value))}
                  inputProps={{ step: "any" }}
                  helperText="GPS coordinate (e.g., 29.8739)"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  select
                  label="Meeting Day"
                  value={formData.meeting_schedule?.meeting_day || ''}
                  onChange={(e) => handleChange('meeting_schedule', 'meeting_day', e.target.value)}
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
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="time"
                  label="Meeting Time"
                  value={formData.meeting_schedule?.meeting_time ? formData.meeting_schedule.meeting_time.substring(0, 5) : ''}
                  onChange={(e) => handleChange('meeting_schedule', 'meeting_time', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                  helperText="Time in 24-hour format"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  select
                  label="Meeting Frequency"
                  value={formData.meeting_schedule?.meeting_frequency || 'WEEKLY'}
                  onChange={(e) => handleChange('meeting_schedule', 'meeting_frequency', e.target.value)}
                >
                  <MenuItem value="WEEKLY">Weekly</MenuItem>
                  <MenuItem value="BIWEEKLY">Bi-weekly</MenuItem>
                  <MenuItem value="MONTHLY">Monthly</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          </TabPanel>

          {/* Financial Settings Tab */}
          <TabPanel value={activeTab} index={2}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  select
                  label="Currency"
                  value={formData.financial_settings?.currency || 'UGX'}
                  onChange={(e) => handleChange('financial_settings', 'currency', e.target.value)}
                >
                  <MenuItem value="UGX">UGX (Ugandan Shilling)</MenuItem>
                  <MenuItem value="RWF">RWF (Rwandan Franc)</MenuItem>
                  <MenuItem value="KES">KES (Kenyan Shilling)</MenuItem>
                  <MenuItem value="TZS">TZS (Tanzanian Shilling)</MenuItem>
                  <MenuItem value="USD">USD (US Dollar)</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Share Value"
                  value={formData.financial_settings?.share_value || ''}
                  onChange={(e) => handleChange('financial_settings', 'share_value', parseFloat(e.target.value))}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Group Savings Target"
                  value={formData.financial_settings?.target_amount || ''}
                  onChange={(e) => handleChange('financial_settings', 'target_amount', parseFloat(e.target.value))}
                  helperText="Overall group savings target amount"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Standard Fine Amount"
                  value={formData.financial_settings?.standard_fine_amount || ''}
                  onChange={(e) => handleChange('financial_settings', 'standard_fine_amount', parseFloat(e.target.value))}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Loan Interest Rate (%)"
                  value={(formData.financial_settings?.loan_interest_rate || 0) * 100}
                  onChange={(e) => handleChange('financial_settings', 'loan_interest_rate', parseFloat(e.target.value) / 100)}
                  inputProps={{ step: 0.1 }}
                />
              </Grid>
            </Grid>
          </TabPanel>

          {/* Activities Tab */}
          <TabPanel value={activeTab} index={3}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Financial Activities</Typography>
              <Button
                variant="outlined"
                startIcon={<SettingsIcon />}
                onClick={() => setManageSavingTypesOpen(true)}
              >
                Manage Saving Types
              </Button>
            </Box>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.financial_activities?.personal_savings?.enabled || false}
                      onChange={(e) => handleChange('financial_activities', 'personal_savings', {
                        ...formData.financial_activities?.personal_savings,
                        enabled: e.target.checked
                      })}
                    />
                  }
                  label="Personal Savings"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.financial_activities?.ecd_fund?.enabled || false}
                      onChange={(e) => handleChange('financial_activities', 'ecd_fund', {
                        ...formData.financial_activities?.ecd_fund,
                        enabled: e.target.checked
                      })}
                    />
                  }
                  label="ECD Fund"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.financial_activities?.social_fund?.enabled || false}
                      onChange={(e) => handleChange('financial_activities', 'social_fund', {
                        ...formData.financial_activities?.social_fund,
                        enabled: e.target.checked
                      })}
                    />
                  }
                  label="Social Fund"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.financial_activities?.emergency_fund?.enabled || false}
                      onChange={(e) => handleChange('financial_activities', 'emergency_fund', {
                        ...formData.financial_activities?.emergency_fund,
                        enabled: e.target.checked
                      })}
                    />
                  }
                  label="Emergency Fund"
                />
              </Grid>
            </Grid>

            <Divider sx={{ my: 3 }} />

            <Typography variant="h6" gutterBottom>Other Activities</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.attendance_tracking?.enabled || false}
                      onChange={(e) => handleChange('attendance_tracking', 'enabled', e.target.checked)}
                    />
                  }
                  label="Attendance Tracking"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.other_activities?.voting_session_enabled || false}
                      onChange={(e) => handleChange('other_activities', 'voting_session_enabled', e.target.checked)}
                    />
                  }
                  label="Voting Sessions"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.other_activities?.training_session_enabled || false}
                      onChange={(e) => handleChange('other_activities', 'training_session_enabled', e.target.checked)}
                    />
                  }
                  label="Training Sessions"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.other_activities?.fine_collection_enabled || false}
                      onChange={(e) => handleChange('other_activities', 'fine_collection_enabled', e.target.checked)}
                    />
                  }
                  label="Fine Collection"
                />
              </Grid>
            </Grid>
          </TabPanel>

          {/* Loan Settings Tab */}
          <TabPanel value={activeTab} index={4}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.loan_activities?.loan_disbursement_enabled || false}
                      onChange={(e) => handleChange('loan_activities', 'loan_disbursement_enabled', e.target.checked)}
                    />
                  }
                  label="Loan Disbursement Enabled"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.loan_activities?.loan_repayment_enabled || false}
                      onChange={(e) => handleChange('loan_activities', 'loan_repayment_enabled', e.target.checked)}
                    />
                  }
                  label="Loan Repayment Enabled"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Max Loan Multiplier"
                  value={formData.loan_activities?.max_loan_multiplier || 3}
                  onChange={(e) => handleChange('loan_activities', 'max_loan_multiplier', parseFloat(e.target.value))}
                  helperText="Maximum loan amount as multiple of savings"
                  inputProps={{ step: 0.5 }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Minimum Months for Loan"
                  value={formData.loan_activities?.min_months_for_loan || 3}
                  onChange={(e) => handleChange('loan_activities', 'min_months_for_loan', parseInt(e.target.value))}
                  helperText="Minimum membership months required"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Minimum Attendance for Loan (%)"
                  value={formData.loan_activities?.min_attendance_for_loan || 75}
                  onChange={(e) => handleChange('loan_activities', 'min_attendance_for_loan', parseFloat(e.target.value))}
                  helperText="Minimum attendance percentage required"
                  inputProps={{ step: 1 }}
                />
              </Grid>
            </Grid>
          </TabPanel>

          {/* Fine Settings Tab */}
          <TabPanel value={activeTab} index={5}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Late Arrival Fine"
                  value={formData.fine_settings?.late_arrival_fine || ''}
                  onChange={(e) => handleChange('fine_settings', 'late_arrival_fine', parseFloat(e.target.value))}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Absence Fine"
                  value={formData.fine_settings?.absence_fine || ''}
                  onChange={(e) => handleChange('fine_settings', 'absence_fine', parseFloat(e.target.value))}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Missed Contribution Fine"
                  value={formData.fine_settings?.missed_contribution_fine || ''}
                  onChange={(e) => handleChange('fine_settings', 'missed_contribution_fine', parseFloat(e.target.value))}
                />
              </Grid>
            </Grid>
          </TabPanel>

          {/* Documents Tab */}
          <TabPanel value={activeTab} index={6}>
            <GroupDocumentsTab
              groupId={groupId}
              isAdmin={currentUser?.admin || false}
            />
          </TabPanel>
        </CardContent>
      </Card>

      {/* Manage Saving Types Dialog */}
      <ManageSavingTypes
        open={manageSavingTypesOpen}
        onClose={() => setManageSavingTypesOpen(false)}
        groupId={groupId}
      />
    </Box>
  );
}

export default GroupSettings;

