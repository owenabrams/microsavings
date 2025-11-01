import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Box,
  Typography,
  Alert,
  CircularProgress,
  InputAdornment,
  IconButton,
  Chip,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Close as CloseIcon,
  AttachFile as AttachFileIcon,
} from '@mui/icons-material';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { remotePaymentsAPI, transactionDocumentsAPI } from '../services/api';

const RemotePaymentDialog = ({ open, onClose, meeting, savingTypes, groupSettings }) => {
  const queryClient = useQueryClient();
  
  const [formData, setFormData] = useState({
    saving_type_id: '',
    amount: '',
    mobile_money_reference: '',
    mobile_money_phone: '',
    description: '',
  });
  
  const [files, setFiles] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Submit remote payment mutation
  const submitMutation = useMutation({
    mutationFn: async (data) => {
      // First, submit the payment
      const response = await remotePaymentsAPI.submitRemotePayment(meeting.id, data);
      const transactionId = response.data.data.transaction_id;
      
      // Then, upload documents if any
      if (files.length > 0) {
        await transactionDocumentsAPI.uploadDocuments('savings', transactionId, files, {
          document_type: 'RECEIPT',
          document_category: 'FINANCIAL',
          description: 'Mobile money payment proof',
          is_proof_document: true,
        });
      }
      
      return response;
    },
    onSuccess: () => {
      setSuccess('Remote payment submitted successfully! Awaiting verification by officers.');
      queryClient.invalidateQueries(['meeting', meeting.id]);
      queryClient.invalidateQueries(['memberDashboard']);
      
      // Reset form
      setTimeout(() => {
        handleClose();
      }, 2000);
    },
    onError: (error) => {
      setError(error.response?.data?.message || 'Failed to submit remote payment');
    },
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    setError('');
  };

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    
    // Validate file types (PDF only)
    const invalidFiles = selectedFiles.filter(file => file.type !== 'application/pdf');
    if (invalidFiles.length > 0) {
      setError('Only PDF files are allowed for proof documents');
      return;
    }
    
    // Validate file size (50MB max)
    const oversizedFiles = selectedFiles.filter(file => file.size > 50 * 1024 * 1024);
    if (oversizedFiles.length > 0) {
      setError('File size must not exceed 50MB');
      return;
    }
    
    setFiles(prev => [...prev, ...selectedFiles]);
    setError('');
  };

  const handleRemoveFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = () => {
    // Validate required fields
    if (!formData.saving_type_id) {
      setError('Please select a saving type');
      return;
    }
    
    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      setError('Please enter a valid amount');
      return;
    }
    
    if (!formData.mobile_money_reference) {
      setError('Please enter the mobile money transaction ID');
      return;
    }
    
    if (!formData.mobile_money_phone) {
      setError('Please enter the phone number used for payment');
      return;
    }
    
    // Submit the payment
    submitMutation.mutate({
      saving_type_id: parseInt(formData.saving_type_id),
      amount: parseFloat(formData.amount),
      mobile_money_reference: formData.mobile_money_reference,
      mobile_money_phone: formData.mobile_money_phone,
      description: formData.description || `Remote payment for ${meeting.meeting_type || 'meeting'}`,
    });
  };

  const handleClose = () => {
    if (!submitMutation.isPending) {
      setFormData({
        saving_type_id: '',
        amount: '',
        mobile_money_reference: '',
        mobile_money_phone: '',
        description: '',
      });
      setFiles([]);
      setError('');
      setSuccess('');
      onClose();
    }
  };

  if (!meeting || !groupSettings) {
    return null;
  }

  const currency = groupSettings.currency || 'UGX';

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">📱 Submit Remote Payment</Typography>
          <IconButton onClick={handleClose} size="small" disabled={submitMutation.isPending}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        {/* Meeting Info */}
        <Box mb={3} p={2} bgcolor="grey.100" borderRadius={1}>
          <Typography variant="body2" color="text.secondary">
            <strong>Meeting:</strong> {meeting.meeting_type || 'Regular Meeting'} #{meeting.meeting_number}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            <strong>Date:</strong> {new Date(meeting.meeting_date).toLocaleDateString()}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            <strong>Location:</strong> {meeting.location || 'Not specified'}
          </Typography>
        </Box>

        {/* Error/Success Messages */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        {/* Form Fields */}
        <Box display="flex" flexDirection="column" gap={2}>
          {/* Saving Type */}
          <FormControl fullWidth required>
            <InputLabel>Saving Type</InputLabel>
            <Select
              name="saving_type_id"
              value={formData.saving_type_id}
              onChange={handleChange}
              label="Saving Type"
              disabled={submitMutation.isPending}
            >
              {savingTypes && savingTypes.map((type) => (
                <MenuItem key={type.id} value={type.id}>
                  {type.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Amount */}
          <TextField
            fullWidth
            required
            label="Amount"
            name="amount"
            type="number"
            value={formData.amount}
            onChange={handleChange}
            disabled={submitMutation.isPending}
            InputProps={{
              startAdornment: <InputAdornment position="start">{currency}</InputAdornment>,
            }}
            helperText="Enter the amount you sent via mobile money"
          />

          {/* Mobile Money Reference */}
          <TextField
            fullWidth
            required
            label="Transaction ID / Reference"
            name="mobile_money_reference"
            value={formData.mobile_money_reference}
            onChange={handleChange}
            disabled={submitMutation.isPending}
            placeholder="e.g., MTN-ABC123456"
            helperText="Enter the mobile money transaction reference number"
          />

          {/* Phone Number */}
          <TextField
            fullWidth
            required
            label="Phone Number"
            name="mobile_money_phone"
            value={formData.mobile_money_phone}
            onChange={handleChange}
            disabled={submitMutation.isPending}
            placeholder="e.g., +256700123456"
            helperText="Enter the phone number you used to send the money"
          />

          {/* Description (Optional) */}
          <TextField
            fullWidth
            label="Description (Optional)"
            name="description"
            value={formData.description}
            onChange={handleChange}
            disabled={submitMutation.isPending}
            multiline
            rows={2}
            placeholder="Add any additional notes..."
          />

          {/* File Upload */}
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              📎 Upload Proof (Optional)
            </Typography>
            <Button
              variant="outlined"
              component="label"
              startIcon={<CloudUploadIcon />}
              disabled={submitMutation.isPending}
              fullWidth
            >
              Choose File (PDF only)
              <input
                type="file"
                hidden
                accept="application/pdf"
                multiple
                onChange={handleFileChange}
              />
            </Button>
            
            {/* Display selected files */}
            {files.length > 0 && (
              <Box mt={1} display="flex" flexWrap="wrap" gap={1}>
                {files.map((file, index) => (
                  <Chip
                    key={index}
                    icon={<AttachFileIcon />}
                    label={file.name}
                    onDelete={() => handleRemoveFile(index)}
                    disabled={submitMutation.isPending}
                    size="small"
                  />
                ))}
              </Box>
            )}
          </Box>

          {/* Important Note */}
          <Alert severity="info" icon="⚠️">
            <Typography variant="body2">
              <strong>Note:</strong> Your payment will be verified by officers before it counts in the meeting totals.
              You will be notified once your payment is verified.
            </Typography>
          </Alert>
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button 
          onClick={handleClose} 
          disabled={submitMutation.isPending}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={submitMutation.isPending}
          startIcon={submitMutation.isPending ? <CircularProgress size={20} /> : null}
        >
          {submitMutation.isPending ? 'Submitting...' : 'Submit for Verification'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RemotePaymentDialog;

