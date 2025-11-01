import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  Breadcrumbs,
  Link,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import EventIcon from '@mui/icons-material/Event';
import HomeIcon from '@mui/icons-material/Home';
import { meetingsAPI, groupsAPI } from '../services/api';
import CreateMeetingDialog from './CreateMeetingDialog';

function MeetingsList() {
  const { groupId } = useParams();
  const navigate = useNavigate();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Fetch group details for breadcrumb
  const { data: groupData } = useQuery({
    queryKey: ['group', groupId],
    queryFn: async () => {
      const response = await groupsAPI.getById(groupId);
      return response.data;
    },
  });

  const { data, isLoading, error } = useQuery({
    queryKey: ['meetings', groupId, statusFilter],
    queryFn: async () => {
      const params = statusFilter !== 'ALL' ? { status: statusFilter } : {};
      const response = await meetingsAPI.getGroupMeetings(groupId, params);
      return response.data;
    },
  });

  const handleTabChange = (event, newValue) => {
    setStatusFilter(newValue);
  };

  const handleMeetingClick = (meetingId) => {
    navigate(`/groups/${groupId}/meetings/${meetingId}`);
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
        Failed to load meetings: {error.message}
      </Alert>
    );
  }

  const meetings = data?.meetings || [];

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

  const getStatusIcon = (status) => {
    switch (status) {
      case 'SCHEDULED':
        return <EventIcon />;
      case 'IN_PROGRESS':
        return <PlayArrowIcon />;
      case 'COMPLETED':
        return <CheckCircleIcon />;
      default:
        return null;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const group = groupData?.data;

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
        <Typography color="text.primary">
          Meetings
        </Typography>
      </Breadcrumbs>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Group Meetings
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Create Meeting
        </Button>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={statusFilter} onChange={handleTabChange}>
          <Tab label="All" value="ALL" />
          <Tab label="Scheduled" value="SCHEDULED" />
          <Tab label="In Progress" value="IN_PROGRESS" />
          <Tab label="Completed" value="COMPLETED" />
        </Tabs>
      </Box>

      {meetings.length === 0 ? (
        <Alert severity="info">
          No meetings found. Create your first meeting to get started.
        </Alert>
      ) : (
        <Grid container spacing={3}>
          {meetings.map((meeting) => (
            <Grid item xs={12} md={6} lg={4} key={meeting.id}>
              <Card 
                sx={{ 
                  cursor: 'pointer',
                  '&:hover': {
                    boxShadow: 6,
                  }
                }}
                onClick={() => handleMeetingClick(meeting.id)}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" gutterBottom>
                      Meeting #{meeting.meeting_number}
                    </Typography>
                    <Chip
                      icon={getStatusIcon(meeting.status)}
                      label={meeting.status}
                      color={getStatusColor(meeting.status)}
                      size="small"
                    />
                  </Box>

                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Date:</strong> {formatDate(meeting.meeting_date)}
                  </Typography>

                  {meeting.meeting_time && (
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      <strong>Time:</strong> {meeting.meeting_time}
                    </Typography>
                  )}

                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Type:</strong> {meeting.meeting_type}
                  </Typography>

                  {meeting.location && (
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      <strong>Location:</strong> {meeting.location}
                    </Typography>
                  )}

                  {meeting.status === 'COMPLETED' && (
                    <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Attendance:</strong> {meeting.members_present}/{meeting.total_members} ({meeting.attendance_rate?.toFixed(1)}%)
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Savings Collected:</strong> {meeting.total_savings_collected?.toLocaleString() || 0}
                      </Typography>
                      {meeting.quorum_met !== undefined && (
                        <Chip
                          label={meeting.quorum_met ? 'Quorum Met' : 'No Quorum'}
                          color={meeting.quorum_met ? 'success' : 'warning'}
                          size="small"
                          sx={{ mt: 1 }}
                        />
                      )}
                    </Box>
                  )}

                  {meeting.agenda && (
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                      <strong>Agenda:</strong> {meeting.agenda.substring(0, 100)}{meeting.agenda.length > 100 ? '...' : ''}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <CreateMeetingDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        groupId={groupId}
      />
    </Box>
  );
}

export default MeetingsList;

