import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Snackbar,
  IconButton,
  Chip,
  Grid,
  CircularProgress,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import SaveIcon from '@mui/icons-material/Save';
import { meetingsAPI, groupsAPI, transactionDocumentsAPI } from '../services/api';
import DocumentUpload from './DocumentUpload';
import RemotePaymentsTab from './RemotePaymentsTab';

const MeetingWorkspace = () => {
  const { meetingId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // Fetch meeting details
  const { data: meeting, isLoading: meetingLoading } = useQuery({
    queryKey: ['meeting', meetingId],
    queryFn: async () => {
      const response = await meetingsAPI.getMeetingDetail(meetingId);
      return response.data.meeting;
    },
  });

  // Fetch group members
  const { data: membersData, isLoading: membersLoading } = useQuery({
    queryKey: ['groupMembers', meeting?.group_id],
    queryFn: async () => {
      const response = await groupsAPI.getMembers(meeting.group_id);
      return response.data.data.members;
    },
    enabled: !!meeting?.group_id,
  });

  // Fetch group details for currency
  const { data: groupData } = useQuery({
    queryKey: ['group', meeting?.group_id],
    queryFn: async () => {
      const response = await groupsAPI.getById(meeting.group_id);
      return response.data.data;
    },
    enabled: !!meeting?.group_id,
  });

  // Fetch saving types
  const { data: savingTypes, isLoading: savingTypesLoading } = useQuery({
    queryKey: ['savingTypes', meeting?.group_id],
    queryFn: async () => {
      const response = await meetingsAPI.getSavingTypes(meeting.group_id);
      return response.data.data;
    },
    enabled: !!meeting?.group_id,
  });

  // State for savings transactions
  const [savingsData, setSavingsData] = useState({});
  const [selectedSavingType, setSelectedSavingType] = useState('');
  const [savingsFiles, setSavingsFiles] = useState({});

  // State for fines
  const [finesData, setFinesData] = useState({});
  const [finesFiles, setFinesFiles] = useState({});

  // State for training
  const [trainingData, setTrainingData] = useState({
    training_topic: '',
    training_description: '',
    trainer_name: '',
    duration_minutes: 60,
  });
  const [trainingAttendance, setTrainingAttendance] = useState({});
  const [createdTrainingId, setCreatedTrainingId] = useState(null);
  const [trainingFiles, setTrainingFiles] = useState([]);

  // State for voting
  const [votingData, setVotingData] = useState({
    vote_topic: '',
    vote_description: '',
    vote_type: 'SIMPLE_MAJORITY',
  });
  const [votes, setVotes] = useState({});
  const [createdVotingId, setCreatedVotingId] = useState(null);
  const [votingFiles, setVotingFiles] = useState([]);

  // Mutations
  const savingsMutation = useMutation({
    mutationFn: (data) => meetingsAPI.recordSavings(meetingId, data),
    onSuccess: () => {
      setSnackbar({ open: true, message: 'Savings transaction recorded successfully', severity: 'success' });
      queryClient.invalidateQueries(['meeting', meetingId]);
    },
    onError: (error) => {
      setSnackbar({ open: true, message: error.response?.data?.message || 'Failed to record savings', severity: 'error' });
    },
  });

  const finesMutation = useMutation({
    mutationFn: (data) => meetingsAPI.recordFines(meetingId, data),
    onSuccess: () => {
      setSnackbar({ open: true, message: 'Fine recorded successfully', severity: 'success' });
      queryClient.invalidateQueries(['meeting', meetingId]);
    },
    onError: (error) => {
      setSnackbar({ open: true, message: error.response?.data?.message || 'Failed to record fine', severity: 'error' });
    },
  });

  const trainingMutation = useMutation({
    mutationFn: (data) => meetingsAPI.createTraining(meetingId, data),
    onSuccess: (response) => {
      const trainingId = response.data.data.training_id;
      setCreatedTrainingId(trainingId);
      setSnackbar({ open: true, message: 'Training session created successfully', severity: 'success' });
    },
    onError: (error) => {
      setSnackbar({ open: true, message: error.response?.data?.message || 'Failed to create training', severity: 'error' });
    },
  });

  const trainingAttendanceMutation = useMutation({
    mutationFn: ({ trainingId, data }) => meetingsAPI.recordTrainingAttendance(trainingId, data),
    onSuccess: () => {
      setSnackbar({ open: true, message: 'Training attendance recorded successfully', severity: 'success' });
      queryClient.invalidateQueries(['meeting', meetingId]);
    },
    onError: (error) => {
      setSnackbar({ open: true, message: error.response?.data?.message || 'Failed to record attendance', severity: 'error' });
    },
  });

  const votingMutation = useMutation({
    mutationFn: (data) => meetingsAPI.createVoting(meetingId, data),
    onSuccess: (response) => {
      const votingId = response.data.data.voting_id;
      setCreatedVotingId(votingId);
      setSnackbar({ open: true, message: 'Voting session created successfully', severity: 'success' });
    },
    onError: (error) => {
      setSnackbar({ open: true, message: error.response?.data?.message || 'Failed to create voting', severity: 'error' });
    },
  });

  const votesMutation = useMutation({
    mutationFn: ({ votingId, data }) => meetingsAPI.recordVotes(votingId, data),
    onSuccess: () => {
      setSnackbar({ open: true, message: 'Votes recorded successfully', severity: 'success' });
      queryClient.invalidateQueries(['meeting', meetingId]);
    },
    onError: (error) => {
      setSnackbar({ open: true, message: error.response?.data?.message || 'Failed to record votes', severity: 'error' });
    },
  });

  // Handlers
  const handleSavingsChange = (memberId, field, value) => {
    setSavingsData(prev => ({
      ...prev,
      [memberId]: {
        ...prev[memberId],
        [field]: value,
      },
    }));
  };

  const handleRecordSavings = async (memberId) => {
    const data = savingsData[memberId];
    const files = savingsFiles[memberId] || [];

    if (!selectedSavingType || (!data?.deposit && !data?.withdrawal)) {
      setSnackbar({ open: true, message: 'Please select saving type and enter amount', severity: 'warning' });
      return;
    }

    try {
      let transactionId = null;

      if (data.deposit) {
        const response = await meetingsAPI.recordSavings(meetingId, {
          member_id: memberId,
          saving_type_id: selectedSavingType,
          transaction_type: 'DEPOSIT',
          amount: parseFloat(data.deposit),
        });
        transactionId = response.data.data.transactions[0].id;
      }

      if (data.withdrawal) {
        const response = await meetingsAPI.recordSavings(meetingId, {
          member_id: memberId,
          saving_type_id: selectedSavingType,
          transaction_type: 'WITHDRAWAL',
          amount: parseFloat(data.withdrawal),
        });
        transactionId = response.data.data.transactions[0].id;
      }

      // Upload documents if any
      if (files.length > 0 && transactionId) {
        await transactionDocumentsAPI.uploadDocuments('savings', transactionId, files, {
          document_type: 'RECEIPT',
          document_category: 'FINANCIAL',
          description: 'Savings transaction proof',
        });
      }

      setSnackbar({ open: true, message: 'Savings transaction recorded successfully', severity: 'success' });
      queryClient.invalidateQueries(['meeting', meetingId]);

      // Clear the row
      setSavingsData(prev => ({
        ...prev,
        [memberId]: {},
      }));
      setSavingsFiles(prev => ({
        ...prev,
        [memberId]: [],
      }));
    } catch (error) {
      setSnackbar({
        open: true,
        message: error.response?.data?.message || 'Failed to record savings',
        severity: 'error'
      });
    }
  };

  const handleFinesChange = (memberId, field, value) => {
    setFinesData(prev => ({
      ...prev,
      [memberId]: {
        ...prev[memberId],
        [field]: value,
      },
    }));
  };

  const handleRecordFine = async (memberId) => {
    const data = finesData[memberId];
    const files = finesFiles[memberId] || [];

    if (!data?.amount || !data?.fine_type) {
      setSnackbar({ open: true, message: 'Please enter fine type and amount', severity: 'warning' });
      return;
    }

    try {
      const response = await meetingsAPI.recordFines(meetingId, {
        member_id: memberId,
        fine_type: data.fine_type,
        amount: parseFloat(data.amount),
        reason: data.reason || '',
      });

      const fineId = response.data.data.fines[0].id;

      // Upload documents if any
      if (files.length > 0 && fineId) {
        await transactionDocumentsAPI.uploadDocuments('fine', fineId, files, {
          document_type: 'RECEIPT',
          document_category: 'FINANCIAL',
          description: 'Fine payment proof',
        });
      }

      setSnackbar({ open: true, message: 'Fine recorded successfully', severity: 'success' });
      queryClient.invalidateQueries(['meeting', meetingId]);

      // Clear the row
      setFinesData(prev => ({
        ...prev,
        [memberId]: {},
      }));
      setFinesFiles(prev => ({
        ...prev,
        [memberId]: [],
      }));
    } catch (error) {
      setSnackbar({
        open: true,
        message: error.response?.data?.message || 'Failed to record fine',
        severity: 'error'
      });
    }
  };

  const handleCreateTraining = async () => {
    if (!trainingData.training_topic) {
      setSnackbar({ open: true, message: 'Please enter training topic', severity: 'warning' });
      return;
    }

    try {
      const response = await meetingsAPI.createTraining(meetingId, trainingData);
      const trainingId = response.data.data.training_id;
      setCreatedTrainingId(trainingId);

      // Upload documents if any
      if (trainingFiles.length > 0 && trainingId) {
        await transactionDocumentsAPI.uploadDocuments('training', trainingId, trainingFiles, {
          document_type: 'REPORT',
          document_category: 'TRAINING',
          description: 'Training session materials',
        });
      }

      setSnackbar({ open: true, message: 'Training session created successfully', severity: 'success' });
      setTrainingFiles([]);
    } catch (error) {
      setSnackbar({
        open: true,
        message: error.response?.data?.message || 'Failed to create training',
        severity: 'error'
      });
    }
  };

  const handleTrainingAttendanceChange = (memberId, attended) => {
    setTrainingAttendance(prev => ({
      ...prev,
      [memberId]: attended,
    }));
  };

  const handleRecordTrainingAttendance = () => {
    if (!createdTrainingId) {
      setSnackbar({ open: true, message: 'Please create training session first', severity: 'warning' });
      return;
    }

    const attendance = Object.entries(trainingAttendance).map(([memberId, attended]) => ({
      member_id: parseInt(memberId),
      attended,
    }));

    trainingAttendanceMutation.mutate({
      trainingId: createdTrainingId,
      data: { attendance },
    });
  };

  const handleCreateVoting = async () => {
    if (!votingData.vote_topic) {
      setSnackbar({ open: true, message: 'Please enter voting topic', severity: 'warning' });
      return;
    }

    try {
      const response = await meetingsAPI.createVoting(meetingId, votingData);
      const votingId = response.data.data.voting_id;
      setCreatedVotingId(votingId);

      // Upload documents if any
      if (votingFiles.length > 0 && votingId) {
        await transactionDocumentsAPI.uploadDocuments('voting', votingId, votingFiles, {
          document_type: 'REPORT',
          document_category: 'VOTING',
          description: 'Voting session documentation',
        });
      }

      setSnackbar({ open: true, message: 'Voting session created successfully', severity: 'success' });
      setVotingFiles([]);
    } catch (error) {
      setSnackbar({
        open: true,
        message: error.response?.data?.message || 'Failed to create voting',
        severity: 'error'
      });
    }
  };

  const handleVoteChange = (memberId, vote) => {
    setVotes(prev => ({
      ...prev,
      [memberId]: vote,
    }));
  };

  const handleRecordVotes = () => {
    if (!createdVotingId) {
      setSnackbar({ open: true, message: 'Please create voting session first', severity: 'warning' });
      return;
    }

    const voteRecords = Object.entries(votes).map(([memberId, vote]) => ({
      member_id: parseInt(memberId),
      vote,
    }));

    votesMutation.mutate({
      votingId: createdVotingId,
      data: { votes: voteRecords },
    });
  };

  if (meetingLoading || membersLoading || savingTypesLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!meeting || meeting.status !== 'IN_PROGRESS') {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="warning">
          This meeting is not in progress. Only meetings in progress can record transactions.
        </Alert>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate(`/groups/${meeting?.group_id}/meetings/${meetingId}`)}
          sx={{ mt: 2 }}
        >
          Back to Meeting
        </Button>
      </Box>
    );
  }

  const members = membersData || [];
  const currency = groupData?.currency || 'UGX';

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate(`/groups/${meeting.group_id}/meetings/${meetingId}`)}
            sx={{ mb: 1 }}
          >
            Back to Meeting
          </Button>
          <Typography variant="h4">Meeting Workspace</Typography>
          <Typography variant="body2" color="text.secondary">
            Meeting #{meeting.meeting_number} - {new Date(meeting.meeting_date).toLocaleDateString()}
          </Typography>
        </Box>
        <Chip label={meeting.status} color="primary" />
      </Box>

      <Card>
        <CardContent>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            <Tab label="Savings" />
            <Tab label="Fines" />
            <Tab label="Training" />
            <Tab label="Voting" />
            <Tab label="📱 Remote Payments" />
          </Tabs>

          {/* Savings Tab */}
          {activeTab === 0 && (
            <Box sx={{ mt: 3 }}>
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Select Saving Type</InputLabel>
                <Select
                  value={selectedSavingType}
                  onChange={(e) => setSelectedSavingType(e.target.value)}
                  label="Select Saving Type"
                >
                  {savingTypes?.filter(st => st.is_enabled).map((type) => (
                    <MenuItem key={type.id} value={type.id}>
                      {type.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {selectedSavingType && (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Member</TableCell>
                        <TableCell>Deposit ({currency})</TableCell>
                        <TableCell>Withdrawal ({currency})</TableCell>
                        <TableCell>Documents</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {members.map((member) => (
                        <TableRow key={member.id}>
                          <TableCell>
                            {member.first_name} {member.last_name}
                          </TableCell>
                          <TableCell>
                            <TextField
                              type="number"
                              size="small"
                              value={savingsData[member.id]?.deposit || ''}
                              onChange={(e) => handleSavingsChange(member.id, 'deposit', e.target.value)}
                              inputProps={{ min: 0, step: 100 }}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              type="number"
                              size="small"
                              value={savingsData[member.id]?.withdrawal || ''}
                              onChange={(e) => handleSavingsChange(member.id, 'withdrawal', e.target.value)}
                              inputProps={{ min: 0, step: 100 }}
                            />
                          </TableCell>
                          <TableCell>
                            <DocumentUpload
                              onFilesSelected={(files) => {
                                setSavingsFiles(prev => ({
                                  ...prev,
                                  [member.id]: files,
                                }));
                              }}
                              maxFiles={3}
                              maxFileSize={10 * 1024 * 1024}
                              showPreview={false}
                            />
                          </TableCell>
                          <TableCell>
                            <Button
                              size="small"
                              variant="contained"
                              startIcon={<SaveIcon />}
                              onClick={() => handleRecordSavings(member.id)}
                              disabled={savingsMutation.isPending}
                            >
                              Save
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>
          )}

          {/* Fines Tab */}
          {activeTab === 1 && (
            <Box sx={{ mt: 3 }}>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Member</TableCell>
                      <TableCell>Fine Type</TableCell>
                      <TableCell>Amount ({currency})</TableCell>
                      <TableCell>Reason</TableCell>
                      <TableCell>Documents</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {members.map((member) => (
                      <TableRow key={member.id}>
                        <TableCell>
                          {member.first_name} {member.last_name}
                        </TableCell>
                        <TableCell>
                          <Select
                            size="small"
                            fullWidth
                            value={finesData[member.id]?.fine_type || ''}
                            onChange={(e) => handleFinesChange(member.id, 'fine_type', e.target.value)}
                          >
                            <MenuItem value="LATE_ARRIVAL">Late Arrival</MenuItem>
                            <MenuItem value="ABSENCE">Absence</MenuItem>
                            <MenuItem value="MISSED_CONTRIBUTION">Missed Contribution</MenuItem>
                            <MenuItem value="RULE_VIOLATION">Rule Violation</MenuItem>
                            <MenuItem value="OTHER">Other</MenuItem>
                          </Select>
                        </TableCell>
                        <TableCell>
                          <TextField
                            type="number"
                            size="small"
                            value={finesData[member.id]?.amount || ''}
                            onChange={(e) => handleFinesChange(member.id, 'amount', e.target.value)}
                            inputProps={{ min: 0, step: 100 }}
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            size="small"
                            fullWidth
                            value={finesData[member.id]?.reason || ''}
                            onChange={(e) => handleFinesChange(member.id, 'reason', e.target.value)}
                            placeholder="Optional"
                          />
                        </TableCell>
                        <TableCell>
                          <DocumentUpload
                            onFilesSelected={(files) => {
                              setFinesFiles(prev => ({
                                ...prev,
                                [member.id]: files,
                              }));
                            }}
                            maxFiles={3}
                            maxFileSize={10 * 1024 * 1024}
                            showPreview={false}
                          />
                        </TableCell>
                        <TableCell>
                          <Button
                            size="small"
                            variant="contained"
                            startIcon={<SaveIcon />}
                            onClick={() => handleRecordFine(member.id)}
                            disabled={finesMutation.isPending}
                          >
                            Save
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Training Tab */}
          {activeTab === 2 && (
            <Box sx={{ mt: 3 }}>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12}>
                  <Typography variant="h6">Create Training Session</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Training Topic"
                    value={trainingData.training_topic}
                    onChange={(e) => setTrainingData({ ...trainingData, training_topic: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    label="Trainer Name"
                    value={trainingData.trainer_name}
                    onChange={(e) => setTrainingData({ ...trainingData, trainer_name: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Duration (minutes)"
                    value={trainingData.duration_minutes}
                    onChange={(e) => setTrainingData({ ...trainingData, duration_minutes: parseInt(e.target.value) })}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={2}
                    label="Description"
                    value={trainingData.training_description}
                    onChange={(e) => setTrainingData({ ...trainingData, training_description: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Training Materials (Optional)
                  </Typography>
                  <DocumentUpload
                    onFilesSelected={setTrainingFiles}
                    maxFiles={5}
                    maxFileSize={20 * 1024 * 1024}
                    showPreview={true}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button
                    variant="contained"
                    onClick={handleCreateTraining}
                    disabled={trainingMutation.isPending || createdTrainingId}
                  >
                    {createdTrainingId ? 'Training Session Created' : 'Create Training Session'}
                  </Button>
                </Grid>
              </Grid>

              {createdTrainingId && (
                <>
                  <Typography variant="h6" sx={{ mb: 2 }}>Record Attendance</Typography>
                  <TableContainer component={Paper}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Member</TableCell>
                          <TableCell>Attended</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {members.map((member) => (
                          <TableRow key={member.id}>
                            <TableCell>
                              {member.first_name} {member.last_name}
                            </TableCell>
                            <TableCell>
                              <Select
                                size="small"
                                value={trainingAttendance[member.id] !== undefined ? trainingAttendance[member.id] : true}
                                onChange={(e) => handleTrainingAttendanceChange(member.id, e.target.value)}
                              >
                                <MenuItem value={true}>Yes</MenuItem>
                                <MenuItem value={false}>No</MenuItem>
                              </Select>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                  <Button
                    variant="contained"
                    onClick={handleRecordTrainingAttendance}
                    disabled={trainingAttendanceMutation.isPending}
                    sx={{ mt: 2 }}
                  >
                    Save Attendance
                  </Button>
                </>
              )}
            </Box>
          )}

          {/* Voting Tab */}
          {activeTab === 3 && (
            <Box sx={{ mt: 3 }}>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12}>
                  <Typography variant="h6">Create Voting Session</Typography>
                </Grid>
                <Grid item xs={12} md={8}>
                  <TextField
                    fullWidth
                    label="Vote Topic"
                    value={votingData.vote_topic}
                    onChange={(e) => setVotingData({ ...votingData, vote_topic: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth>
                    <InputLabel>Vote Type</InputLabel>
                    <Select
                      value={votingData.vote_type}
                      onChange={(e) => setVotingData({ ...votingData, vote_type: e.target.value })}
                      label="Vote Type"
                    >
                      <MenuItem value="SIMPLE_MAJORITY">Simple Majority</MenuItem>
                      <MenuItem value="TWO_THIRDS">Two-Thirds Majority</MenuItem>
                      <MenuItem value="UNANIMOUS">Unanimous</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={2}
                    label="Description"
                    value={votingData.vote_description}
                    onChange={(e) => setVotingData({ ...votingData, vote_description: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Supporting Documents (Optional)
                  </Typography>
                  <DocumentUpload
                    onFilesSelected={setVotingFiles}
                    maxFiles={5}
                    maxFileSize={20 * 1024 * 1024}
                    showPreview={true}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button
                    variant="contained"
                    onClick={handleCreateVoting}
                    disabled={votingMutation.isPending || createdVotingId}
                  >
                    {createdVotingId ? 'Voting Session Created' : 'Create Voting Session'}
                  </Button>
                </Grid>
              </Grid>

              {createdVotingId && (
                <>
                  <Typography variant="h6" sx={{ mb: 2 }}>Record Votes</Typography>
                  <TableContainer component={Paper}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Member</TableCell>
                          <TableCell>Vote</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {members.map((member) => (
                          <TableRow key={member.id}>
                            <TableCell>
                              {member.first_name} {member.last_name}
                            </TableCell>
                            <TableCell>
                              <Select
                                size="small"
                                value={votes[member.id] || 'ABSTAIN'}
                                onChange={(e) => handleVoteChange(member.id, e.target.value)}
                              >
                                <MenuItem value="YES">Yes</MenuItem>
                                <MenuItem value="NO">No</MenuItem>
                                <MenuItem value="ABSTAIN">Abstain</MenuItem>
                              </Select>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                  <Button
                    variant="contained"
                    onClick={handleRecordVotes}
                    disabled={votesMutation.isPending}
                    sx={{ mt: 2 }}
                  >
                    Save Votes
                  </Button>
                </>
              )}
            </Box>
          )}

          {/* Remote Payments Tab */}
          {activeTab === 4 && (
            <Box sx={{ mt: 3 }}>
              <RemotePaymentsTab meetingId={meetingId} currency={currency} />
            </Box>
          )}
        </CardContent>
      </Card>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default MeetingWorkspace;

