import React, { useState } from 'react';
import { useParams, useNavigate, Link as RouterLink } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Box, Card, CardContent, Typography, Button, CircularProgress,
  Alert, Tabs, Tab, Grid, Chip, Avatar, Divider, List, ListItem,
  ListItemText, IconButton, Breadcrumbs, Link, Paper, Table,
  TableBody, TableCell, TableContainer, TableHead, TableRow
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import EditIcon from '@mui/icons-material/Edit';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PersonIcon from '@mui/icons-material/Person';
import PhoneIcon from '@mui/icons-material/Phone';
import EmailIcon from '@mui/icons-material/Email';
import HomeIcon from '@mui/icons-material/Home';
import BadgeIcon from '@mui/icons-material/Badge';
import WorkIcon from '@mui/icons-material/Work';
import CakeIcon from '@mui/icons-material/Cake';
import { membersAPI } from '../services/api';
import MemberSettings from './MemberSettings';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

function MemberProfile() {
  const { groupId, memberId } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const [settingsOpen, setSettingsOpen] = useState(false);

  // Fetch member profile
  const { data: profileData, isLoading: profileLoading, error: profileError, refetch: refetchProfile } = useQuery({
    queryKey: ['memberProfile', groupId, memberId],
    queryFn: async () => {
      const response = await membersAPI.getProfile(groupId, memberId);
      return response.data.data;
    }
  });

  // Fetch financial data
  const { data: financialData, isLoading: financialLoading } = useQuery({
    queryKey: ['memberFinancial', groupId, memberId],
    queryFn: async () => {
      const response = await membersAPI.getFinancial(groupId, memberId);
      return response.data.data;
    },
    enabled: activeTab === 1 // Only fetch when Financial tab is active
  });

  // Fetch attendance data
  const { data: attendanceData, isLoading: attendanceLoading } = useQuery({
    queryKey: ['memberAttendance', groupId, memberId],
    queryFn: async () => {
      const response = await membersAPI.getAttendance(groupId, memberId);
      return response.data.data;
    },
    enabled: activeTab === 2 // Only fetch when Attendance tab is active
  });

  // Fetch activity log
  const { data: activityData, isLoading: activityLoading } = useQuery({
    queryKey: ['memberActivity', groupId, memberId],
    queryFn: async () => {
      const response = await membersAPI.getActivityLog(groupId, memberId);
      return response.data.data;
    },
    enabled: activeTab === 4 // Only fetch when Activity tab is active
  });

  // Fetch documents
  const { data: documentsData, isLoading: documentsLoading, refetch: refetchDocuments } = useQuery({
    queryKey: ['memberDocuments', groupId, memberId],
    queryFn: async () => {
      const response = await membersAPI.getDocuments(groupId, memberId);
      return response.data.data;
    },
    enabled: activeTab === 3 // Only fetch when Documents tab is active
  });

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleSettingsClose = () => {
    setSettingsOpen(false);
    refetchProfile();
  };

  if (profileLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (profileError) {
    return (
      <Box>
        <Button onClick={() => navigate(`/groups/${groupId}`)} startIcon={<ArrowBackIcon />} sx={{ mb: 2 }}>
          Back to Group
        </Button>
        <Alert severity="error">
          Failed to load member profile: {profileError.message}
        </Alert>
      </Box>
    );
  }

  const member = profileData || {};
  const activities = activityData?.activities || [];
  const documents = documentsData || [];

  const getStatusColor = (status) => {
    switch (status) {
      case 'ACTIVE': return 'success';
      case 'INACTIVE': return 'default';
      case 'SUSPENDED': return 'error';
      default: return 'default';
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'FOUNDER': return 'primary';
      case 'OFFICER': return 'secondary';
      default: return 'default';
    }
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
          {member.group_name}
        </Link>
        <Typography color="text.primary">
          {member.first_name} {member.last_name}
        </Typography>
      </Breadcrumbs>

      {/* Header Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Avatar
                sx={{ width: 80, height: 80, bgcolor: 'primary.main', fontSize: '2rem' }}
                src={member.profile_photo_url}
              >
                {member.first_name?.[0]}{member.last_name?.[0]}
              </Avatar>
              <Box>
                <Typography variant="h4" gutterBottom>
                  {member.first_name} {member.last_name}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                  <Chip
                    label={member.status || 'ACTIVE'}
                    color={getStatusColor(member.status)}
                    size="small"
                  />
                  <Chip
                    label={member.role || 'MEMBER'}
                    color={getRoleColor(member.role)}
                    size="small"
                  />
                  {member.is_eligible_for_loans && (
                    <Chip label="Loan Eligible" color="success" size="small" variant="outlined" />
                  )}
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Member since {member.joined_date ? new Date(member.joined_date).toLocaleDateString() : 'N/A'}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="outlined"
                startIcon={<DashboardIcon />}
                onClick={() => navigate(`/dashboard/member/${memberId}`)}
              >
                View Dashboard
              </Button>
              <Button
                variant="contained"
                startIcon={<EditIcon />}
                onClick={() => setSettingsOpen(true)}
              >
                Edit Profile
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Card>
        <Tabs value={activeTab} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}>
          <Tab label="Overview" />
          <Tab label="Financial" />
          <Tab label="Attendance" />
          <Tab label="Documents" />
          <Tab label="Activity Log" />
        </Tabs>

        <CardContent>
          {/* Overview Tab */}
          <TabPanel value={activeTab} index={0}>
            <Grid container spacing={3}>
              {/* Personal Information */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>Personal Information</Typography>
                <List>
                  <ListItem>
                    <PersonIcon sx={{ mr: 2, color: 'text.secondary' }} />
                    <ListItemText
                      primary="Full Name"
                      secondary={`${member.first_name} ${member.last_name}`}
                    />
                  </ListItem>
                  <ListItem>
                    <EmailIcon sx={{ mr: 2, color: 'text.secondary' }} />
                    <ListItemText
                      primary="Email"
                      secondary={member.email || 'Not provided'}
                    />
                  </ListItem>
                  <ListItem>
                    <PhoneIcon sx={{ mr: 2, color: 'text.secondary' }} />
                    <ListItemText
                      primary="Phone Number"
                      secondary={member.phone_number || 'Not provided'}
                    />
                  </ListItem>
                  <ListItem>
                    <BadgeIcon sx={{ mr: 2, color: 'text.secondary' }} />
                    <ListItemText
                      primary="ID Number"
                      secondary={member.id_number || 'Not provided'}
                    />
                  </ListItem>
                  <ListItem>
                    <CakeIcon sx={{ mr: 2, color: 'text.secondary' }} />
                    <ListItemText
                      primary="Date of Birth"
                      secondary={member.date_of_birth ? new Date(member.date_of_birth).toLocaleDateString() : 'Not provided'}
                    />
                  </ListItem>
                  <ListItem>
                    <WorkIcon sx={{ mr: 2, color: 'text.secondary' }} />
                    <ListItemText
                      primary="Occupation"
                      secondary={member.occupation || 'Not provided'}
                    />
                  </ListItem>
                  <ListItem>
                    <HomeIcon sx={{ mr: 2, color: 'text.secondary' }} />
                    <ListItemText
                      primary="Address"
                      secondary={member.address || 'Not provided'}
                    />
                  </ListItem>
                </List>
              </Grid>

              {/* Financial Summary */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>Financial Summary</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="text.secondary" gutterBottom>
                          Share Balance
                        </Typography>
                        <Typography variant="h5">
                          {member.group_currency} {parseFloat(member.share_balance || 0).toLocaleString()}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={6}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="text.secondary" gutterBottom>
                          Total Contributions
                        </Typography>
                        <Typography variant="h5">
                          {member.group_currency} {parseFloat(member.total_contributions || 0).toLocaleString()}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={6}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="text.secondary" gutterBottom>
                          Attendance Rate
                        </Typography>
                        <Typography variant="h5">
                          {parseFloat(member.attendance_percentage || 0).toFixed(1)}%
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={6}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="text.secondary" gutterBottom>
                          Documents
                        </Typography>
                        <Typography variant="h5">
                          {member.document_count || 0}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                {member.emergency_contact_name && (
                  <>
                    <Divider sx={{ my: 3 }} />
                    <Typography variant="h6" gutterBottom>Emergency Contact</Typography>
                    <List>
                      <ListItem>
                        <ListItemText
                          primary="Name"
                          secondary={member.emergency_contact_name}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Phone"
                          secondary={member.emergency_contact_phone || 'Not provided'}
                        />
                      </ListItem>
                    </List>
                  </>
                )}
              </Grid>
            </Grid>
          </TabPanel>

          {/* Financial Tab */}
          <TabPanel value={activeTab} index={1}>
            {financialLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : financialData ? (
              <Grid container spacing={3}>
                {/* Savings Section */}
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom>Savings by Fund</Typography>
                  <TableContainer component={Paper}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Fund Name</TableCell>
                          <TableCell align="right">Total Deposits</TableCell>
                          <TableCell align="right">Total Withdrawals</TableCell>
                          <TableCell align="right">Balance</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {financialData.savings.by_fund.map((fund, index) => (
                          <TableRow key={index}>
                            <TableCell>
                              <Typography variant="body2" fontWeight="bold">{fund.fund_name}</Typography>
                              <Typography variant="caption" color="text.secondary">{fund.fund_description}</Typography>
                            </TableCell>
                            <TableCell align="right">{parseFloat(fund.total_deposits).toFixed(2)}</TableCell>
                            <TableCell align="right">{parseFloat(fund.total_withdrawals).toFixed(2)}</TableCell>
                            <TableCell align="right">
                              <Typography fontWeight="bold" color="primary">
                                {parseFloat(fund.balance).toFixed(2)}
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ))}
                        <TableRow>
                          <TableCell colSpan={3} align="right"><strong>Total Savings:</strong></TableCell>
                          <TableCell align="right">
                            <Typography variant="h6" color="primary">
                              {parseFloat(financialData.savings.total).toFixed(2)}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Grid>

                {/* Loans Section */}
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom>Loans</Typography>
                  {financialData.loans.length > 0 ? (
                    <TableContainer component={Paper}>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Status</TableCell>
                            <TableCell align="right">Principal</TableCell>
                            <TableCell align="right">Interest Rate</TableCell>
                            <TableCell align="right">Amount Paid</TableCell>
                            <TableCell align="right">Outstanding</TableCell>
                            <TableCell>Application Date</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {financialData.loans.map((loan) => (
                            <TableRow key={loan.id}>
                              <TableCell>
                                <Chip
                                  label={loan.status}
                                  color={loan.status === 'ACTIVE' ? 'success' : loan.status === 'PENDING' ? 'warning' : 'default'}
                                  size="small"
                                />
                              </TableCell>
                              <TableCell align="right">{parseFloat(loan.principal).toFixed(2)}</TableCell>
                              <TableCell align="right">{parseFloat(loan.interest_rate * 100).toFixed(2)}%</TableCell>
                              <TableCell align="right">{parseFloat(loan.amount_paid).toFixed(2)}</TableCell>
                              <TableCell align="right">{parseFloat(loan.outstanding_balance).toFixed(2)}</TableCell>
                              <TableCell>{new Date(loan.application_date).toLocaleDateString()}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  ) : (
                    <Alert severity="info">No loans found for this member.</Alert>
                  )}
                </Grid>

                {/* Fines Section */}
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom>Fines</Typography>
                  <Grid container spacing={2} sx={{ mb: 2 }}>
                    <Grid item xs={4}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="body2" color="text.secondary">Total Fines</Typography>
                        <Typography variant="h6">{parseFloat(financialData.fines.total).toFixed(2)}</Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={4}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="body2" color="text.secondary">Paid</Typography>
                        <Typography variant="h6" color="success.main">{parseFloat(financialData.fines.paid).toFixed(2)}</Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={4}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="body2" color="text.secondary">Outstanding</Typography>
                        <Typography variant="h6" color="error.main">{parseFloat(financialData.fines.outstanding).toFixed(2)}</Typography>
                      </Paper>
                    </Grid>
                  </Grid>
                  {financialData.fines.items.length > 0 ? (
                    <TableContainer component={Paper}>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Type</TableCell>
                            <TableCell>Reason</TableCell>
                            <TableCell align="right">Amount</TableCell>
                            <TableCell align="right">Paid</TableCell>
                            <TableCell>Date</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {financialData.fines.items.map((fine) => (
                            <TableRow key={fine.id}>
                              <TableCell>{fine.fine_type}</TableCell>
                              <TableCell>{fine.reason || 'N/A'}</TableCell>
                              <TableCell align="right">{parseFloat(fine.amount).toFixed(2)}</TableCell>
                              <TableCell align="right">
                                {fine.is_paid ? (
                                  <Chip label="Paid" color="success" size="small" />
                                ) : (
                                  <Chip label="Unpaid" color="error" size="small" />
                                )}
                              </TableCell>
                              <TableCell>{new Date(fine.created_date).toLocaleDateString()}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  ) : (
                    <Alert severity="success">No fines for this member.</Alert>
                  )}
                </Grid>
              </Grid>
            ) : (
              <Alert severity="error">Failed to load financial data.</Alert>
            )}
          </TabPanel>

          {/* Attendance Tab */}
          <TabPanel value={activeTab} index={2}>
            {attendanceLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : attendanceData ? (
              <>
                {/* Summary Cards */}
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="body2" color="text.secondary">Total Meetings</Typography>
                      <Typography variant="h5">{attendanceData.summary.total_meetings}</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="body2" color="text.secondary">Attended</Typography>
                      <Typography variant="h5" color="success.main">{attendanceData.summary.attended}</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="body2" color="text.secondary">Absent</Typography>
                      <Typography variant="h5" color="error.main">{attendanceData.summary.absent}</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="body2" color="text.secondary">Attendance Rate</Typography>
                      <Typography variant="h5" color="primary">{attendanceData.summary.attendance_rate}%</Typography>
                    </Paper>
                  </Grid>
                </Grid>

                {/* Attendance History Table */}
                <Typography variant="h6" gutterBottom>Attendance History</Typography>
                {attendanceData.records.length > 0 ? (
                  <TableContainer component={Paper}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Meeting Date</TableCell>
                          <TableCell>Meeting Type</TableCell>
                          <TableCell>Status</TableCell>
                          <TableCell>Arrival Time</TableCell>
                          <TableCell>Excuse Reason</TableCell>
                          <TableCell align="right">Fine Amount</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {attendanceData.records.map((record) => (
                          <TableRow key={record.id}>
                            <TableCell>{new Date(record.meeting_date).toLocaleDateString()}</TableCell>
                            <TableCell>{record.meeting_type || 'Regular'}</TableCell>
                            <TableCell>
                              <Chip
                                label={record.is_present ? 'Present' : 'Absent'}
                                color={record.is_present ? 'success' : 'error'}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>{record.arrival_time || 'N/A'}</TableCell>
                            <TableCell>{record.excuse_reason || 'N/A'}</TableCell>
                            <TableCell align="right">
                              {record.fine_applied && record.fine_amount ? parseFloat(record.fine_amount).toFixed(2) : '-'}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                ) : (
                  <Alert severity="info">No attendance records found.</Alert>
                )}
              </>
            ) : (
              <Alert severity="error">Failed to load attendance data.</Alert>
            )}
          </TabPanel>

          {/* Documents Tab */}
          <TabPanel value={activeTab} index={3}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Documents</Typography>
              <Button variant="outlined" size="small">
                Upload Document
              </Button>
            </Box>
            {documentsLoading ? (
              <CircularProgress />
            ) : documents.length === 0 ? (
              <Alert severity="info">No documents uploaded yet.</Alert>
            ) : (
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Document Name</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Uploaded Date</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {documents.map((doc) => (
                      <TableRow key={doc.id}>
                        <TableCell>{doc.document_name}</TableCell>
                        <TableCell>{doc.document_type}</TableCell>
                        <TableCell>{new Date(doc.uploaded_date).toLocaleDateString()}</TableCell>
                        <TableCell>
                          <Chip
                            label={doc.is_verified ? 'Verified' : 'Pending'}
                            color={doc.is_verified ? 'success' : 'warning'}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </TabPanel>

          {/* Activity Log Tab */}
          <TabPanel value={activeTab} index={4}>
            <Typography variant="h6" gutterBottom>Activity Log</Typography>
            {activityLoading ? (
              <CircularProgress />
            ) : activities.length === 0 ? (
              <Alert severity="info">No activity recorded yet.</Alert>
            ) : (
              <List>
                {activities.map((activity) => (
                  <React.Fragment key={activity.id}>
                    <ListItem alignItems="flex-start">
                      <ListItemText
                        primary={activity.description}
                        secondary={
                          <>
                            <Typography component="span" variant="body2" color="text.primary">
                              {activity.activity_type}
                            </Typography>
                            {' — '}
                            {new Date(activity.activity_date).toLocaleString()}
                            {activity.performed_by_username && ` by ${activity.performed_by_username}`}
                          </>
                        }
                      />
                    </ListItem>
                    <Divider component="li" />
                  </React.Fragment>
                ))}
              </List>
            )}
          </TabPanel>
        </CardContent>
      </Card>

      {/* Member Settings Modal */}
      <MemberSettings
        open={settingsOpen}
        onClose={handleSettingsClose}
        groupId={groupId}
        memberId={memberId}
      />
    </Box>
  );
}

export default MemberProfile;

