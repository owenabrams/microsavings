import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Switch,
  FormControlLabel,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Typography,
  Chip,
  Box,
  Alert,
  Divider,
  Tooltip
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';
import WarningIcon from '@mui/icons-material/Warning';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';

function ManageSavingTypes({ open, onClose, groupId }) {
  const queryClient = useQueryClient();
  const [editMode, setEditMode] = useState(false);
  const [selectedType, setSelectedType] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    code: '',
    is_mandatory: false,
    minimum_amount: '',
    maximum_amount: '',
    allows_withdrawal: true,
    withdrawal_notice_days: 0,
    interest_rate: 0
  });
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [usageData, setUsageData] = useState(null);

  // Fetch saving types
  const { data: savingTypes, isLoading } = useQuery({
    queryKey: ['savingTypes', groupId],
    queryFn: async () => {
      const response = await api.get(`/api/groups/${groupId}/saving-types`);
      return response.data.data;
    },
    enabled: open
  });

  // Create mutation
  const createMutation = useMutation({
    mutationFn: async (data) => {
      const response = await api.post(`/api/groups/${groupId}/saving-types`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['savingTypes', groupId]);
      queryClient.invalidateQueries(['groupSettings', groupId]);
      resetForm();
    }
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: async ({ typeId, data }) => {
      const response = await api.put(`/api/groups/${groupId}/saving-types/${typeId}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['savingTypes', groupId]);
      queryClient.invalidateQueries(['groupSettings', groupId]);
      resetForm();
    }
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (typeId) => {
      const response = await api.delete(`/api/groups/${groupId}/saving-types/${typeId}`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['savingTypes', groupId]);
      queryClient.invalidateQueries(['groupSettings', groupId]);
      setDeleteConfirm(null);
      setUsageData(null);
    }
  });

  // Fetch usage data before delete
  const fetchUsage = async (typeId) => {
    try {
      const response = await api.get(`/api/groups/${groupId}/saving-types/${typeId}/usage`);
      setUsageData(response.data.data);
    } catch (error) {
      console.error('Error fetching usage:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      code: '',
      is_mandatory: false,
      minimum_amount: '',
      maximum_amount: '',
      allows_withdrawal: true,
      withdrawal_notice_days: 0,
      interest_rate: 0
    });
    setEditMode(false);
    setSelectedType(null);
  };

  const handleEdit = (type) => {
    setSelectedType(type);
    setFormData({
      name: type.name,
      description: type.description || '',
      code: type.code,
      is_mandatory: type.is_mandatory,
      minimum_amount: type.minimum_amount || '',
      maximum_amount: type.maximum_amount || '',
      allows_withdrawal: type.allows_withdrawal,
      withdrawal_notice_days: type.withdrawal_notice_days || 0,
      interest_rate: (type.interest_rate || 0) * 100
    });
    setEditMode(true);
  };

  const handleDelete = async (type) => {
    if (type.is_system) {
      alert('System saving types cannot be deleted. You can disable them instead.');
      return;
    }
    setDeleteConfirm(type);
    await fetchUsage(type.id);
  };

  const confirmDelete = () => {
    if (deleteConfirm) {
      deleteMutation.mutate(deleteConfirm.id);
    }
  };

  const handleSubmit = () => {
    const submitData = {
      ...formData,
      interest_rate: parseFloat(formData.interest_rate) / 100,
      minimum_amount: formData.minimum_amount ? parseFloat(formData.minimum_amount) : null,
      maximum_amount: formData.maximum_amount ? parseFloat(formData.maximum_amount) : null
    };

    if (selectedType) {
      updateMutation.mutate({ typeId: selectedType.id, data: submitData });
    } else {
      createMutation.mutate(submitData);
    }
  };

  const handleToggleEnabled = (type) => {
    updateMutation.mutate({
      typeId: type.id,
      data: { is_enabled: !type.is_enabled }
    });
  };

  return (
    <>
      <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
        <DialogTitle>
          Manage Financial Activities
          <Typography variant="body2" color="text.secondary">
            Add custom saving types or configure existing ones
          </Typography>
        </DialogTitle>
        <DialogContent>
          {isLoading ? (
            <Typography>Loading...</Typography>
          ) : (
            <Box>
              {/* Add/Edit Form */}
              {editMode && (
                <Box sx={{ mb: 3, p: 2, bgcolor: 'background.paper', border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                  <Typography variant="h6" gutterBottom>
                    {selectedType ? 'Edit Saving Type' : 'Add New Saving Type'}
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Name"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        disabled={selectedType?.is_system}
                        required
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Code"
                        value={formData.code}
                        onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
                        disabled={selectedType?.is_system}
                        helperText="Auto-generated if left empty"
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        multiline
                        rows={2}
                        label="Description"
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        disabled={selectedType?.is_system}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        type="number"
                        label="Minimum Amount"
                        value={formData.minimum_amount}
                        onChange={(e) => setFormData({ ...formData, minimum_amount: e.target.value })}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        type="number"
                        label="Maximum Amount"
                        value={formData.maximum_amount}
                        onChange={(e) => setFormData({ ...formData, maximum_amount: e.target.value })}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        type="number"
                        label="Interest Rate (%)"
                        value={formData.interest_rate}
                        onChange={(e) => setFormData({ ...formData, interest_rate: e.target.value })}
                        inputProps={{ step: 0.1 }}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        type="number"
                        label="Withdrawal Notice (days)"
                        value={formData.withdrawal_notice_days}
                        onChange={(e) => setFormData({ ...formData, withdrawal_notice_days: e.target.value })}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={formData.allows_withdrawal}
                            onChange={(e) => setFormData({ ...formData, allows_withdrawal: e.target.checked })}
                          />
                        }
                        label="Allows Withdrawal"
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={formData.is_mandatory}
                            onChange={(e) => setFormData({ ...formData, is_mandatory: e.target.checked })}
                            disabled={selectedType?.is_system}
                          />
                        }
                        label="Mandatory for all members"
                      />
                    </Grid>
                  </Grid>
                  <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                    <Button variant="contained" onClick={handleSubmit} disabled={!formData.name}>
                      {selectedType ? 'Update' : 'Create'}
                    </Button>
                    <Button onClick={resetForm}>Cancel</Button>
                  </Box>
                </Box>
              )}

              {!editMode && (
                <Button
                  variant="outlined"
                  startIcon={<AddIcon />}
                  onClick={() => setEditMode(true)}
                  sx={{ mb: 2 }}
                >
                  Add New Saving Type
                </Button>
              )}

              <Divider sx={{ my: 2 }} />

              {/* List of Saving Types */}
              <Typography variant="h6" gutterBottom>
                Existing Saving Types
              </Typography>
              <List>
                {savingTypes?.map((type) => (
                  <ListItem
                    key={type.id}
                    sx={{
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 1,
                      mb: 1,
                      bgcolor: type.is_enabled ? 'background.paper' : 'action.disabledBackground'
                    }}
                  >
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {type.name}
                          {type.is_system && <Chip label="System" size="small" color="primary" />}
                          {type.is_mandatory && <Chip label="Mandatory" size="small" />}
                          {!type.is_enabled && <Chip label="Disabled" size="small" color="default" />}
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2">{type.description}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            Code: {type.code} | 
                            {type.minimum_amount && ` Min: ${type.minimum_amount} |`}
                            {type.maximum_amount && ` Max: ${type.maximum_amount} |`}
                            {type.interest_rate > 0 && ` Interest: ${(type.interest_rate * 100).toFixed(2)}%`}
                          </Typography>
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Tooltip title={type.is_enabled ? "Disable" : "Enable"}>
                        <Switch
                          checked={type.is_enabled}
                          onChange={() => handleToggleEnabled(type)}
                          size="small"
                        />
                      </Tooltip>
                      <IconButton onClick={() => handleEdit(type)} size="small">
                        <EditIcon />
                      </IconButton>
                      {type.can_delete && (
                        <IconButton onClick={() => handleDelete(type)} size="small" color="error">
                          <DeleteIcon />
                        </IconButton>
                      )}
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteConfirm} onClose={() => setDeleteConfirm(null)}>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <WarningIcon color="warning" />
            Confirm Deletion
          </Box>
        </DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This action cannot be undone!
          </Alert>
          <Typography gutterBottom>
            Are you sure you want to delete <strong>{deleteConfirm?.name}</strong>?
          </Typography>
          {usageData && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>Impact:</Typography>
              <Typography variant="body2">• {usageData.members_using} members using this saving type</Typography>
              <Typography variant="body2">• Total balance: {usageData.total_balance.toLocaleString()}</Typography>
              <Typography variant="body2">• {usageData.total_transactions} transactions will be deleted</Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirm(null)}>Cancel</Button>
          <Button onClick={confirmDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default ManageSavingTypes;

