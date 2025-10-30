import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Grid,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Breadcrumbs,
  Link,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import PeopleIcon from '@mui/icons-material/People';
import WorkIcon from '@mui/icons-material/Work';
import HomeIcon from '@mui/icons-material/Home';
import { meetingsAPI, groupsAPI } from '../services/api';
import RecordAttendanceDialog from './RecordAttendanceDialog';
import DocumentManager from './DocumentManager';
import EditSavingsTransactionDialog from './EditSavingsTransactionDialog';
import EditFineDialog from './EditFineDialog';
import EditLoanRepaymentDialog from './EditLoanRepaymentDialog';
import EditTrainingDialog from './EditTrainingDialog';
import EditVotingDialog from './EditVotingDialog';

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

function MeetingDetailEnhanced() {
  const { groupId, meetingId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [attendanceDialogOpen, setAttendanceDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [editFormData, setEditFormData] = useState({});

  // Edit transaction dialogs
  const [editSavingsDialog, setEditSavingsDialog] = useState({ open: false, transaction: null });
  const [editFineDialog, setEditFineDialog] = useState({ open: false, fine: null });
  const [editLoanDialog, setEditLoanDialog] = useState({ open: false, repayment: null });
  const [editTrainingDialog, setEditTrainingDialog] = useState({ open: false, training: null });
  const [editVotingDialog, setEditVotingDialog] = useState({ open: false, voting: null });

  const { data, isLoading, error } = useQuery({
    queryKey: ['meeting', meetingId],
    queryFn: async () => {
      const response = await meetingsAPI.getMeetingDetail(meetingId);
      return response.data;
    },
  });

  // Fetch group details for currency
  const { data: groupData } = useQuery({
    queryKey: ['group', groupId],
    queryFn: async () => {
      const response = await groupsAPI.getById(groupId);
      return response.data.data;
    },
    enabled: !!groupId,
  });

  const startMutation = useMutation({
    mutationFn: () => meetingsAPI.startMeeting(meetingId),
    onSuccess: () => {
      queryClient.invalidateQueries(['meeting', meetingId]);
      queryClient.invalidateQueries(['meetings', groupId]);
    },
  });

  const completeMutation = useMutation({
    mutationFn: () => meetingsAPI.completeMeeting(meetingId),
    onSuccess: () => {
      queryClient.invalidateQueries(['meeting', meetingId]);
      queryClient.invalidateQueries(['meetings', groupId]);
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data) => meetingsAPI.updateMeeting(meetingId, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['meeting', meetingId]);
      queryClient.invalidateQueries(['meetings', groupId]);
      setEditDialogOpen(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => meetingsAPI.deleteMeeting(meetingId),
    onSuccess: () => {
      queryClient.invalidateQueries(['meetings', groupId]);
      navigate(`/groups/${groupId}/meetings`);
    },
  });

  const handleBack = () => {
    navigate(`/groups/${groupId}/meetings`);
  };

  const handleStartMeeting = () => {
    if (window.confirm('Are you sure you want to start this meeting?')) {
      startMutation.mutate();
    }
  };

  const handleCompleteMeeting = () => {
    if (window.confirm('Are you sure you want to complete this meeting? This will calculate all summaries.')) {
      completeMutation.mutate();
    }
  };

  const handleEdit = () => {
    setEditFormData({
      meeting_date: meeting.meeting_date,
      meeting_time: meeting.meeting_time,
      location: meeting.location,
      agenda: meeting.agenda,
      minutes: meeting.minutes,
      decisions_made: meeting.decisions_made,
      action_items: meeting.action_items,
    });
    setEditDialogOpen(true);
  };

  const handleSaveEdit = () => {
    updateMutation.mutate(editFormData);
  };

  const handleDelete = () => {
    if (window.confirm('⚠️ WARNING: This will permanently delete this meeting and ALL associated records (attendance, transactions, fines, trainings, votings). This action CANNOT be undone. Are you absolutely sure?')) {
      deleteMutation.mutate();
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load meeting details: {error.message}
      </Alert>
    );
  }

  const meeting = data?.meeting || {};
  const groupSettings = data?.group_settings || {};
  const attendance = data?.attendance || [];
  const savingsTransactions = data?.savings_transactions || [];
  const fines = data?.fines || [];
  const loanRepayments = data?.loan_repayments || [];
  const trainings = data?.trainings || [];
  const votings = data?.votings || [];
  const summary = data?.summary || {};
  const group = groupData;
  const currency = groupData?.currency || 'UGX';

  const getStatusColor = (status) => {
    switch (status) {
      case 'SCHEDULED':
        return 'info';
      case 'IN_PROGRESS':
        return 'warning';
      case 'COMPLETED':
        return 'success';
      case 'CANCELLED':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatCurrency = (amount) => {
    return `${currency} ${parseFloat(amount || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  return (
    <Box>
      {/* Breadcrumbs */}
      <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 3 }}>
        <Link
          underline="hover"
          sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}
          color="inherit"
          onClick={() => navigate('/dashboard')}
        >
          <HomeIcon sx={{ mr: 0.5 }} fontSize="inherit" />
          Dashboard
        </Link>
        <Link
          underline="hover"
          color="inherit"
          sx={{ cursor: 'pointer' }}
          onClick={() => navigate('/groups')}
        >
          Groups
        </Link>
        <Link
          underline="hover"
          color="inherit"
          sx={{ cursor: 'pointer' }}
          onClick={() => navigate(`/groups/${groupId}`)}
        >
          {group?.name || 'Group'}
        </Link>
        <Link
          underline="hover"
          color="inherit"
          sx={{ cursor: 'pointer' }}
          onClick={() => navigate(`/groups/${groupId}/meetings`)}
        >
          Meetings
        </Link>
        <Typography color="text.primary">
          Meeting #{meeting.meeting_number}
        </Typography>
      </Breadcrumbs>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton onClick={handleBack}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h4" component="h1">
            Meeting #{meeting.meeting_number}
          </Typography>
          <Chip
            label={meeting.status}
            color={getStatusColor(meeting.status)}
            size="small"
          />
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          {meeting.status === 'SCHEDULED' && (
            <Button
              variant="contained"
              color="primary"
              startIcon={<PlayArrowIcon />}
              onClick={handleStartMeeting}
              disabled={startMutation.isLoading}
            >
              Start Meeting
            </Button>
          )}
          {meeting.status === 'IN_PROGRESS' && (
            <>
              <Button
                variant="contained"
                color="primary"
                onClick={() => navigate(`/meetings/${meetingId}/workspace`)}
                startIcon={<WorkIcon />}
              >
                Meeting Workspace
              </Button>
              <Button
                variant="outlined"
                startIcon={<PeopleIcon />}
                onClick={() => setAttendanceDialogOpen(true)}
              >
                Record Attendance
              </Button>
              <Button
                variant="contained"
                color="success"
                startIcon={<CheckCircleIcon />}
                onClick={handleCompleteMeeting}
                disabled={completeMutation.isLoading}
              >
                Complete Meeting
              </Button>
            </>
          )}
          <Button
            variant="outlined"
            startIcon={<EditIcon />}
            onClick={handleEdit}
          >
            Edit
          </Button>
          <Button
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleDelete}
            disabled={deleteMutation.isLoading}
          >
            Delete
          </Button>
        </Box>
      </Box>

      {/* Meeting Information Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Meeting Information
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                Date
              </Typography>
              <Typography variant="body1">{formatDate(meeting.meeting_date)}</Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                Time
              </Typography>
              <Typography variant="body1">{meeting.meeting_time || 'N/A'}</Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                Type
              </Typography>
              <Typography variant="body1">{meeting.meeting_type || 'N/A'}</Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                Location
              </Typography>
              <Typography variant="body1">{meeting.location || 'N/A'}</Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                Attendance
              </Typography>
              <Typography variant="body1">
                {meeting.members_present || 0} / {meeting.total_members || 0} members
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                Quorum Status
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip
                  label={meeting.quorum_met ? 'Quorum Met' : 'No Quorum'}
                  color={meeting.quorum_met ? 'success' : 'error'}
                  size="small"
                />
              </Box>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="body2" color="text.secondary">
                Agenda
              </Typography>
              <Typography variant="body1">{meeting.agenda || 'N/A'}</Typography>
            </Grid>
            {meeting.status === 'COMPLETED' && (
              <>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    Minutes
                  </Typography>
                  <Typography variant="body1">{meeting.minutes || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    Decisions Made
                  </Typography>
                  <Typography variant="body1">{meeting.decisions_made || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    Action Items
                  </Typography>
                  <Typography variant="body1">{meeting.action_items || 'N/A'}</Typography>
                </Grid>
              </>
            )}
          </Grid>
        </CardContent>
      </Card>

      {/* Meeting Summary Card - Only show if completed */}
      {meeting.status === 'COMPLETED' && summary && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Meeting Summary
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Total Deposits
                </Typography>
                <Typography variant="h6" color="success.main">
                  {formatCurrency(summary.total_deposits)}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Total Withdrawals
                </Typography>
                <Typography variant="h6" color="error.main">
                  {formatCurrency(summary.total_withdrawals)}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Net Savings
                </Typography>
                <Typography variant="h6" color="primary.main">
                  {formatCurrency(summary.net_savings)}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Fines Issued
                </Typography>
                <Typography variant="body1">
                  {formatCurrency(summary.total_fines_issued)}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Fines Paid
                </Typography>
                <Typography variant="body1">
                  {formatCurrency(summary.total_fines_paid)}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Loan Repayments
                </Typography>
                <Typography variant="body1">
                  {formatCurrency(summary.total_loan_repayments)}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Trainings Held
                </Typography>
                <Typography variant="body1">{summary.trainings_held || 0}</Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Voting Sessions
                </Typography>
                <Typography variant="body1">{summary.voting_sessions_held || 0}</Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">
                  Net Cash Flow
                </Typography>
                <Typography variant="h6" color={summary.net_cash_flow >= 0 ? 'success.main' : 'error.main'}>
                  {formatCurrency(summary.net_cash_flow)}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Detailed Transactions Tabs */}
      <Card>
        <CardContent>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            <Tab label={`Attendance (${attendance.length})`} />
            <Tab label={`Savings (${savingsTransactions.length})`} />
            <Tab label={`Fines (${fines.length})`} />
            <Tab label={`Loan Repayments (${loanRepayments.length})`} />
            <Tab label={`Trainings (${trainings.length})`} />
            <Tab label={`Votings (${votings.length})`} />
          </Tabs>

          {/* Attendance Tab */}
          <TabPanel value={activeTab} index={0}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Member Name</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Arrival Time</TableCell>
                    <TableCell>Excuse Reason</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {attendance.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={4} align="center">
                        No attendance records yet
                      </TableCell>
                    </TableRow>
                  ) : (
                    attendance.map((record) => (
                      <TableRow key={record.id}>
                        <TableCell>{record.member_name}</TableCell>
                        <TableCell>
                          <Chip
                            label={record.is_present ? 'Present' : 'Absent'}
                            color={record.is_present ? 'success' : 'error'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{record.arrival_time || 'N/A'}</TableCell>
                        <TableCell>{record.excuse_reason || '-'}</TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>

          {/* Savings Transactions Tab */}
          <TabPanel value={activeTab} index={1}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Member Name</TableCell>
                    <TableCell>Saving Type</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell align="right">Amount</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {savingsTransactions.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        No savings transactions recorded
                      </TableCell>
                    </TableRow>
                  ) : (
                    savingsTransactions.map((transaction) => (
                      <TableRow key={transaction.id}>
                        <TableCell>{transaction.member_name}</TableCell>
                        <TableCell>{transaction.saving_type_name}</TableCell>
                        <TableCell>
                          <Chip
                            label={transaction.transaction_type}
                            color={transaction.transaction_type === 'DEPOSIT' ? 'success' : 'warning'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="right">{formatCurrency(transaction.amount)}</TableCell>
                        <TableCell>{formatDate(transaction.transaction_date)}</TableCell>
                        <TableCell>
                          <Chip
                            label={transaction.verification_status}
                            color={transaction.verification_status === 'VERIFIED' ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="center">
                          <Tooltip title="Edit Transaction">
                            <IconButton
                              size="small"
                              onClick={() => setEditSavingsDialog({ open: true, transaction })}
                            >
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>

          {/* Fines Tab */}
          <TabPanel value={activeTab} index={2}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Member Name</TableCell>
                    <TableCell>Fine Type</TableCell>
                    <TableCell>Reason</TableCell>
                    <TableCell align="right">Amount</TableCell>
                    <TableCell align="right">Paid</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {fines.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        No fines recorded
                      </TableCell>
                    </TableRow>
                  ) : (
                    fines.map((fine) => (
                      <TableRow key={fine.id}>
                        <TableCell>{fine.member_name}</TableCell>
                        <TableCell>{fine.fine_type}</TableCell>
                        <TableCell>{fine.reason}</TableCell>
                        <TableCell align="right">{formatCurrency(fine.amount)}</TableCell>
                        <TableCell align="right">{formatCurrency(fine.paid_amount)}</TableCell>
                        <TableCell>
                          <Chip
                            label={fine.is_paid ? 'Paid' : 'Unpaid'}
                            color={fine.is_paid ? 'success' : 'error'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="center">
                          <Tooltip title="Edit Fine">
                            <IconButton
                              size="small"
                              onClick={() => setEditFineDialog({ open: true, fine })}
                            >
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>

          {/* Loan Repayments Tab */}
          <TabPanel value={activeTab} index={3}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Member Name</TableCell>
                    <TableCell align="right">Repayment Amount</TableCell>
                    <TableCell align="right">Principal</TableCell>
                    <TableCell align="right">Interest</TableCell>
                    <TableCell align="right">Outstanding Balance</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {loanRepayments.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        No loan repayments recorded
                      </TableCell>
                    </TableRow>
                  ) : (
                    loanRepayments.map((repayment) => (
                      <TableRow key={repayment.id}>
                        <TableCell>{repayment.member_name}</TableCell>
                        <TableCell align="right">{formatCurrency(repayment.repayment_amount)}</TableCell>
                        <TableCell align="right">{formatCurrency(repayment.principal_amount)}</TableCell>
                        <TableCell align="right">{formatCurrency(repayment.interest_amount)}</TableCell>
                        <TableCell align="right">{formatCurrency(repayment.outstanding_balance)}</TableCell>
                        <TableCell>{formatDate(repayment.repayment_date)}</TableCell>
                        <TableCell align="center">
                          <Tooltip title="Edit Loan Repayment">
                            <IconButton
                              size="small"
                              onClick={() => setEditLoanDialog({ open: true, repayment })}
                            >
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>

          {/* Trainings Tab */}
          <TabPanel value={activeTab} index={4}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Topic</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Trainer</TableCell>
                    <TableCell>Duration (min)</TableCell>
                    <TableCell>Attendees</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {trainings.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} align="center">
                        No training sessions recorded
                      </TableCell>
                    </TableRow>
                  ) : (
                    trainings.map((training) => (
                      <TableRow key={training.id}>
                        <TableCell>{training.training_topic}</TableCell>
                        <TableCell>{training.training_description || '-'}</TableCell>
                        <TableCell>{training.trainer_name || '-'}</TableCell>
                        <TableCell>{training.duration_minutes || '-'}</TableCell>
                        <TableCell>{training.total_attendees || 0}</TableCell>
                        <TableCell align="center">
                          <Tooltip title="Edit Training">
                            <IconButton
                              size="small"
                              onClick={() => setEditTrainingDialog({ open: true, training })}
                            >
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>

          {/* Votings Tab */}
          <TabPanel value={activeTab} index={5}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Topic</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Result</TableCell>
                    <TableCell align="center">Yes</TableCell>
                    <TableCell align="center">No</TableCell>
                    <TableCell align="center">Abstain</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {votings.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} align="center">
                        No voting sessions recorded
                      </TableCell>
                    </TableRow>
                  ) : (
                    votings.map((voting) => (
                      <TableRow key={voting.id}>
                        <TableCell>{voting.vote_topic}</TableCell>
                        <TableCell>{voting.vote_description || '-'}</TableCell>
                        <TableCell>{voting.vote_type}</TableCell>
                        <TableCell>
                          <Chip
                            label={voting.result}
                            color={voting.result === 'PASSED' ? 'success' : voting.result === 'FAILED' ? 'error' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="center">{voting.yes_count}</TableCell>
                        <TableCell align="center">{voting.no_count}</TableCell>
                        <TableCell align="center">{voting.abstain_count}</TableCell>
                        <TableCell align="center">
                          <Tooltip title="Edit Voting">
                            <IconButton
                              size="small"
                              onClick={() => setEditVotingDialog({ open: true, voting })}
                            >
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Edit Meeting</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Meeting Date"
              type="date"
              value={editFormData.meeting_date || ''}
              onChange={(e) => setEditFormData({ ...editFormData, meeting_date: e.target.value })}
              InputLabelProps={{ shrink: true }}
              fullWidth
            />
            <TextField
              label="Meeting Time"
              type="time"
              value={editFormData.meeting_time || ''}
              onChange={(e) => setEditFormData({ ...editFormData, meeting_time: e.target.value })}
              InputLabelProps={{ shrink: true }}
              fullWidth
            />
            <TextField
              label="Location"
              value={editFormData.location || ''}
              onChange={(e) => setEditFormData({ ...editFormData, location: e.target.value })}
              fullWidth
            />
            <TextField
              label="Agenda"
              value={editFormData.agenda || ''}
              onChange={(e) => setEditFormData({ ...editFormData, agenda: e.target.value })}
              multiline
              rows={3}
              fullWidth
            />
            <TextField
              label="Minutes"
              value={editFormData.minutes || ''}
              onChange={(e) => setEditFormData({ ...editFormData, minutes: e.target.value })}
              multiline
              rows={4}
              fullWidth
            />
            <TextField
              label="Decisions Made"
              value={editFormData.decisions_made || ''}
              onChange={(e) => setEditFormData({ ...editFormData, decisions_made: e.target.value })}
              multiline
              rows={3}
              fullWidth
            />
            <TextField
              label="Action Items"
              value={editFormData.action_items || ''}
              onChange={(e) => setEditFormData({ ...editFormData, action_items: e.target.value })}
              multiline
              rows={3}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveEdit} variant="contained" disabled={updateMutation.isLoading}>
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>

      {/* Record Attendance Dialog */}
      <RecordAttendanceDialog
        open={attendanceDialogOpen}
        onClose={() => setAttendanceDialogOpen(false)}
        meetingId={meetingId}
        groupId={groupId}
      />

      {/* Edit Transaction Dialogs */}
      <EditSavingsTransactionDialog
        open={editSavingsDialog.open}
        onClose={() => setEditSavingsDialog({ open: false, transaction: null })}
        transaction={editSavingsDialog.transaction}
        savingTypes={data?.saving_types || []}
        currency={groupData?.currency || 'UGX'}
      />

      <EditFineDialog
        open={editFineDialog.open}
        onClose={() => setEditFineDialog({ open: false, fine: null })}
        fine={editFineDialog.fine}
        currency={groupData?.currency || 'UGX'}
      />

      <EditLoanRepaymentDialog
        open={editLoanDialog.open}
        onClose={() => setEditLoanDialog({ open: false, repayment: null })}
        repayment={editLoanDialog.repayment}
        currency={groupData?.currency || 'UGX'}
      />

      <EditTrainingDialog
        open={editTrainingDialog.open}
        onClose={() => setEditTrainingDialog({ open: false, training: null })}
        training={editTrainingDialog.training}
      />

      <EditVotingDialog
        open={editVotingDialog.open}
        onClose={() => setEditVotingDialog({ open: false, voting: null })}
        voting={editVotingDialog.voting}
      />
    </Box>
  );
}

export default MeetingDetailEnhanced;

