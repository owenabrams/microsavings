import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  Divider,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Visibility as VisibilityIcon,
  AttachFile as AttachFileIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { remotePaymentsAPI, transactionDocumentsAPI } from '../services/api';

const RemotePaymentsTab = ({ meetingId, currency }) => {
  const queryClient = useQueryClient();
  const [verifyDialog, setVerifyDialog] = useState({ open: false, payment: null, action: null });
  const [notes, setNotes] = useState('');
  const [error, setError] = useState('');

  // Fetch pending payments
  const { data, isLoading, error: fetchError } = useQuery({
    queryKey: ['pendingPayments', meetingId],
    queryFn: async () => {
      const response = await remotePaymentsAPI.getPendingPayments(meetingId);
      return response.data.data;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Verify/Reject mutation
  const verifyMutation = useMutation({
    mutationFn: async ({ transactionId, action, notes }) => {
      return await remotePaymentsAPI.verifyPayment(transactionId, action, notes);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['pendingPayments', meetingId]);
      queryClient.invalidateQueries(['meeting', meetingId]);
      setVerifyDialog({ open: false, payment: null, action: null });
      setNotes('');
      setError('');
    },
    onError: (error) => {
      setError(error.response?.data?.message || 'Failed to process payment');
    },
  });

  const handleOpenVerifyDialog = (payment, action) => {
    setVerifyDialog({ open: true, payment, action });
    setNotes('');
    setError('');
  };

  const handleCloseVerifyDialog = () => {
    if (!verifyMutation.isPending) {
      setVerifyDialog({ open: false, payment: null, action: null });
      setNotes('');
      setError('');
    }
  };

  const handleConfirmAction = () => {
    if (verifyDialog.action === 'REJECT' && !notes.trim()) {
      setError('Please provide a reason for rejection');
      return;
    }

    verifyMutation.mutate({
      transactionId: verifyDialog.payment.id,
      action: verifyDialog.action,
      notes: notes.trim() || undefined,
    });
  };

  const handleViewDocument = async (documentId) => {
    try {
      const response = await transactionDocumentsAPI.getDocument(documentId);
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
    } catch (error) {
      console.error('Error viewing document:', error);
      setError('Failed to view document');
    }
  };

  const formatCurrency = (amount) => {
    return `${currency} ${parseFloat(amount || 0).toLocaleString('en-US', { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 2 
    })}`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
        <CircularProgress />
      </Box>
    );
  }

  if (fetchError) {
    return (
      <Alert severity="error">
        {fetchError.response?.data?.message || 'Failed to load remote payments'}
      </Alert>
    );
  }

  const {
    pending_payments = [],
    verified_payments = [],
    rejected_payments = [],
    pending_count = 0,
    verified_count = 0,
    rejected_count = 0,
    total_pending_amount = 0,
    total_verified_amount = 0,
  } = data || {};

  const PaymentCard = ({ payment, status }) => (
    <Card sx={{ mb: 2, border: status === 'PENDING' ? '2px solid #ff9800' : '1px solid #e0e0e0' }}>
      <CardContent>
        <Grid container spacing={2}>
          {/* Header */}
          <Grid item xs={12}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Box display="flex" alignItems="center" gap={1}>
                <Typography variant="h6">
                  {payment.member_name}
                </Typography>
                <Chip
                  label="📱 Remote"
                  size="small"
                  color="primary"
                  variant="outlined"
                />
                {status === 'PENDING' && (
                  <Chip label="⏳ PENDING" size="small" color="warning" />
                )}
                {status === 'VERIFIED' && (
                  <Chip label="✅ VERIFIED" size="small" color="success" />
                )}
                {status === 'REJECTED' && (
                  <Chip label="❌ REJECTED" size="small" color="error" />
                )}
              </Box>
              <Typography 
                variant="h6" 
                color={status === 'VERIFIED' ? 'success.main' : status === 'PENDING' ? 'warning.main' : 'error.main'}
              >
                {formatCurrency(payment.amount)}
              </Typography>
            </Box>
          </Grid>

          {/* Payment Details */}
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">
              <strong>Saving Type:</strong> {payment.saving_type_name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>Transaction ID:</strong> {payment.mobile_money_reference}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>Phone Number:</strong> {payment.mobile_money_phone}
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">
              <strong>Submitted:</strong> {formatDate(payment.submitted_date)}
            </Typography>
            {payment.verified_date && (
              <Typography variant="body2" color="text.secondary">
                <strong>{status === 'VERIFIED' ? 'Verified' : 'Rejected'}:</strong> {formatDate(payment.verified_date)}
              </Typography>
            )}
            {payment.description && (
              <Typography variant="body2" color="text.secondary">
                <strong>Description:</strong> {payment.description}
              </Typography>
            )}
          </Grid>

          {/* Documents */}
          {payment.documents && payment.documents.length > 0 && (
            <Grid item xs={12}>
              <Box display="flex" alignItems="center" gap={1} flexWrap="wrap">
                <AttachFileIcon fontSize="small" color="action" />
                <Typography variant="body2" color="text.secondary">
                  <strong>Proof Documents:</strong>
                </Typography>
                {payment.documents.map((doc) => (
                  <Tooltip key={doc.id} title="Click to view">
                    <Chip
                      label={doc.file_name}
                      size="small"
                      icon={<VisibilityIcon />}
                      onClick={() => handleViewDocument(doc.id)}
                      clickable
                    />
                  </Tooltip>
                ))}
              </Box>
            </Grid>
          )}

          {/* Notes */}
          {payment.notes && (
            <Grid item xs={12}>
              <Alert severity={status === 'VERIFIED' ? 'success' : 'error'} icon={false}>
                <Typography variant="body2">
                  <strong>Notes:</strong> {payment.notes}
                </Typography>
              </Alert>
            </Grid>
          )}

          {/* Actions (only for PENDING) */}
          {status === 'PENDING' && (
            <Grid item xs={12}>
              <Box display="flex" gap={1} justifyContent="flex-end">
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<CancelIcon />}
                  onClick={() => handleOpenVerifyDialog(payment, 'REJECT')}
                  size="small"
                >
                  Reject
                </Button>
                <Button
                  variant="contained"
                  color="success"
                  startIcon={<CheckCircleIcon />}
                  onClick={() => handleOpenVerifyDialog(payment, 'VERIFY')}
                  size="small"
                >
                  Verify
                </Button>
              </Box>
            </Grid>
          )}
        </Grid>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      {/* Summary Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card sx={{ bgcolor: '#fff3e0', border: '2px solid #ff9800' }}>
            <CardContent>
              <Typography variant="h6" color="warning.main">
                ⏳ Pending Verification
              </Typography>
              <Typography variant="h4">{pending_count}</Typography>
              <Typography variant="body2" color="text.secondary">
                Total: {formatCurrency(total_pending_amount)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ bgcolor: '#e8f5e9' }}>
            <CardContent>
              <Typography variant="h6" color="success.main">
                ✅ Verified
              </Typography>
              <Typography variant="h4">{verified_count}</Typography>
              <Typography variant="body2" color="text.secondary">
                Total: {formatCurrency(total_verified_amount)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ bgcolor: '#ffebee' }}>
            <CardContent>
              <Typography variant="h6" color="error.main">
                ❌ Rejected
              </Typography>
              <Typography variant="h4">{rejected_count}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Pending Payments Section */}
      {pending_count > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            ⏳ Pending Verification ({pending_count})
          </Typography>
          <Divider sx={{ mb: 2 }} />
          {pending_payments.map((payment) => (
            <PaymentCard key={payment.id} payment={payment} status="PENDING" />
          ))}
        </Box>
      )}

      {pending_count === 0 && (
        <Alert severity="info" sx={{ mb: 4 }}>
          No pending remote payments. All payments have been processed.
        </Alert>
      )}

      {/* Verified Payments Section */}
      {verified_count > 0 && (
        <Accordion sx={{ mb: 2 }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">
              ✅ Verified Payments ({verified_count})
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            {verified_payments.map((payment) => (
              <PaymentCard key={payment.id} payment={payment} status="VERIFIED" />
            ))}
          </AccordionDetails>
        </Accordion>
      )}

      {/* Rejected Payments Section */}
      {rejected_count > 0 && (
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">
              ❌ Rejected Payments ({rejected_count})
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            {rejected_payments.map((payment) => (
              <PaymentCard key={payment.id} payment={payment} status="REJECTED" />
            ))}
          </AccordionDetails>
        </Accordion>
      )}

      {/* Verify/Reject Dialog */}
      <Dialog open={verifyDialog.open} onClose={handleCloseVerifyDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {verifyDialog.action === 'VERIFY' ? '✅ Verify Payment' : '❌ Reject Payment'}
        </DialogTitle>
        <DialogContent>
          {verifyDialog.payment && (
            <Box>
              <Typography variant="body1" gutterBottom>
                <strong>Member:</strong> {verifyDialog.payment.member_name}
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>Amount:</strong> {formatCurrency(verifyDialog.payment.amount)}
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>Transaction ID:</strong> {verifyDialog.payment.mobile_money_reference}
              </Typography>
              <Divider sx={{ my: 2 }} />
              
              {error && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
                  {error}
                </Alert>
              )}

              <TextField
                fullWidth
                multiline
                rows={3}
                label={verifyDialog.action === 'VERIFY' ? 'Notes (Optional)' : 'Reason for Rejection (Required)'}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                disabled={verifyMutation.isPending}
                placeholder={
                  verifyDialog.action === 'VERIFY'
                    ? 'e.g., Confirmed with MTN statement'
                    : 'e.g., Transaction ID not found in mobile money records'
                }
                required={verifyDialog.action === 'REJECT'}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseVerifyDialog} disabled={verifyMutation.isPending}>
            Cancel
          </Button>
          <Button
            onClick={handleConfirmAction}
            variant="contained"
            color={verifyDialog.action === 'VERIFY' ? 'success' : 'error'}
            disabled={verifyMutation.isPending}
            startIcon={verifyMutation.isPending ? <CircularProgress size={20} /> : null}
          >
            {verifyMutation.isPending
              ? 'Processing...'
              : verifyDialog.action === 'VERIFY'
              ? 'Confirm Verification'
              : 'Confirm Rejection'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RemotePaymentsTab;

