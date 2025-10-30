import React, { useState, useMemo } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  TextField,
  InputAdornment,
  MenuItem,
  IconButton,
  Tooltip,
  Menu,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import SettingsIcon from '@mui/icons-material/Settings';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import PersonIcon from '@mui/icons-material/Person';
import DashboardIcon from '@mui/icons-material/Dashboard';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import { groupsAPI } from '../services/api';

function GroupDetail() {
  const { groupId } = useParams();
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedMember, setSelectedMember] = useState(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ['group', groupId],
    queryFn: async () => {
      const response = await groupsAPI.getById(groupId);
      return response.data;
    },
  });

  // Extract data before any early returns
  const group = data?.data || {};
  const members = group.members || [];
  const financialSummary = group.financial_summary || {};

  // Filter and search members - must be called before any early returns
  const filteredMembers = useMemo(() => {
    return members.filter(member => {
      const matchesSearch = searchTerm === '' ||
        `${member.first_name} ${member.last_name}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (member.phone_number && member.phone_number.includes(searchTerm)) ||
        (member.email && member.email.toLowerCase().includes(searchTerm.toLowerCase()));

      const matchesRole = roleFilter === '' || member.role === roleFilter;
      const matchesStatus = statusFilter === '' || member.status === statusFilter;

      return matchesSearch && matchesRole && matchesStatus;
    });
  }, [members, searchTerm, roleFilter, statusFilter]);

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Button component={Link} to="/groups" startIcon={<ArrowBackIcon />} sx={{ mb: 2 }}>
          Back to Groups
        </Button>
        <Alert severity="error">
          Failed to load group details: {error.message}
        </Alert>
      </Box>
    );
  }

  const handleMenuOpen = (event, member) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setSelectedMember(member);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedMember(null);
  };

  const handleViewProfile = () => {
    if (selectedMember) {
      navigate(`/groups/${groupId}/members/${selectedMember.id}/profile`);
    }
    handleMenuClose();
  };

  const handleViewDashboard = () => {
    if (selectedMember) {
      navigate(`/dashboard/member/${selectedMember.id}`);
    }
    handleMenuClose();
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Button component={Link} to="/groups" startIcon={<ArrowBackIcon />}>
          Back to Groups
        </Button>
        <Button
          component={Link}
          to={`/groups/${groupId}/settings`}
          variant="outlined"
          startIcon={<SettingsIcon />}
        >
          Group Settings
        </Button>
      </Box>

      <Typography variant="h4" component="h1" gutterBottom>
        {group.name}
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Group Information
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={4}>
                  <Typography variant="body2" color="text.secondary">
                    Status
                  </Typography>
                  <Chip
                    label={group.status || 'ACTIVE'}
                    color={group.status === 'ACTIVE' ? 'success' : 'default'}
                    size="small"
                  />
                </Grid>
                <Grid item xs={6} sm={4}>
                  <Typography variant="body2" color="text.secondary">
                    Members
                  </Typography>
                  <Typography variant="body1">
                    {members.length}{group.max_members ? ` / ${group.max_members}` : ''}
                  </Typography>
                </Grid>
                {group.formation_date && (
                  <Grid item xs={6} sm={4}>
                    <Typography variant="body2" color="text.secondary">
                      Formation Date
                    </Typography>
                    <Typography variant="body1">
                      {new Date(group.formation_date).toLocaleDateString()}
                    </Typography>
                  </Grid>
                )}
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    Location
                  </Typography>
                  <Typography variant="body1">
                    {group.village}, {group.parish}, {group.district}
                    {group.region && `, ${group.region}`}
                    {group.country && `, ${group.country}`}
                  </Typography>
                </Grid>
                {group.meeting_location && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">
                      Meeting Location
                    </Typography>
                    <Typography variant="body1">
                      {group.meeting_location}
                    </Typography>
                  </Grid>
                )}
                {group.meeting_frequency && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">
                      Meeting Schedule
                    </Typography>
                    <Typography variant="body1">
                      {group.meeting_frequency}
                      {group.meeting_day && ` - Day ${group.meeting_day}`}
                      {group.meeting_time && ` at ${group.meeting_time}`}
                    </Typography>
                  </Grid>
                )}
                {group.currency && (
                  <Grid item xs={6} sm={4}>
                    <Typography variant="body2" color="text.secondary">
                      Currency
                    </Typography>
                    <Typography variant="body1">
                      {group.currency}
                    </Typography>
                  </Grid>
                )}
                {group.share_value && (
                  <Grid item xs={6} sm={4}>
                    <Typography variant="body2" color="text.secondary">
                      Share Value
                    </Typography>
                    <Typography variant="body1">
                      {group.currency || 'RWF'} {parseFloat(group.share_value).toLocaleString()}
                    </Typography>
                  </Grid>
                )}
                {group.saving_cycle_months && (
                  <Grid item xs={6} sm={4}>
                    <Typography variant="body2" color="text.secondary">
                      Saving Cycle
                    </Typography>
                    <Typography variant="body1">
                      {group.saving_cycle_months} months
                    </Typography>
                  </Grid>
                )}
                {group.is_registered && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">
                      Registration
                    </Typography>
                    <Typography variant="body1">
                      {group.registration_authority}
                      {group.certificate_number && ` - ${group.certificate_number}`}
                    </Typography>
                  </Grid>
                )}
                {group.description && (
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                      Description
                    </Typography>
                    <Typography variant="body1">
                      {group.description}
                    </Typography>
                  </Grid>
                )}
              </Grid>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Members ({filteredMembers.length})
                </Typography>
                <Button variant="outlined" size="small" startIcon={<PersonIcon />}>
                  Add Member
                </Button>
              </Box>

              {/* Search and Filters */}
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    size="small"
                    placeholder="Search members..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <SearchIcon />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>
                <Grid item xs={12} sm={3}>
                  <TextField
                    fullWidth
                    select
                    size="small"
                    label="Role"
                    value={roleFilter}
                    onChange={(e) => setRoleFilter(e.target.value)}
                  >
                    <MenuItem value="">All Roles</MenuItem>
                    <MenuItem value="FOUNDER">Founder</MenuItem>
                    <MenuItem value="OFFICER">Officer</MenuItem>
                    <MenuItem value="MEMBER">Member</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={3}>
                  <TextField
                    fullWidth
                    select
                    size="small"
                    label="Status"
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                  >
                    <MenuItem value="">All Status</MenuItem>
                    <MenuItem value="ACTIVE">Active</MenuItem>
                    <MenuItem value="INACTIVE">Inactive</MenuItem>
                    <MenuItem value="SUSPENDED">Suspended</MenuItem>
                  </TextField>
                </Grid>
              </Grid>

              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Role</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Phone</TableCell>
                      <TableCell align="right">Contributions</TableCell>
                      <TableCell align="right">Attendance</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredMembers.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={7} align="center">
                          <Typography color="text.secondary" sx={{ py: 2 }}>
                            {searchTerm || roleFilter || statusFilter ? 'No members match your filters' : 'No members yet'}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredMembers.map((member) => (
                        <TableRow
                          key={member.id}
                          hover
                          sx={{ cursor: 'pointer' }}
                          onClick={() => navigate(`/groups/${groupId}/members/${member.id}/profile`)}
                        >
                          <TableCell>
                            <Typography
                              color="primary"
                              sx={{ fontWeight: 500, '&:hover': { textDecoration: 'underline' } }}
                            >
                              {member.first_name} {member.last_name}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={member.role}
                              size="small"
                              color={member.role === 'FOUNDER' ? 'primary' : member.role === 'OFFICER' ? 'secondary' : 'default'}
                            />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={member.status || 'ACTIVE'}
                              size="small"
                              color={member.status === 'ACTIVE' ? 'success' : member.status === 'SUSPENDED' ? 'error' : 'default'}
                            />
                          </TableCell>
                          <TableCell>{member.phone_number || 'N/A'}</TableCell>
                          <TableCell align="right">
                            {group.currency || 'RWF'} {parseFloat(member.total_contributions || 0).toLocaleString()}
                          </TableCell>
                          <TableCell align="right">
                            {parseFloat(member.attendance_percentage || 0).toFixed(1)}%
                          </TableCell>
                          <TableCell align="center">
                            <Tooltip title="More actions">
                              <IconButton
                                size="small"
                                onClick={(e) => handleMenuOpen(e, member)}
                              >
                                <MoreVertIcon />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>

          {/* Member Actions Menu */}
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={handleViewProfile}>
              <PersonIcon sx={{ mr: 1 }} fontSize="small" />
              View Profile
            </MenuItem>
            <MenuItem onClick={handleViewDashboard}>
              <DashboardIcon sx={{ mr: 1 }} fontSize="small" />
              View Dashboard
            </MenuItem>
          </Menu>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Financial Summary
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Total Savings
                </Typography>
                <Typography variant="h5" color="success.main">
                  {group.currency || 'RWF'} {parseFloat(financialSummary.total_savings || 0).toLocaleString()}
                </Typography>
              </Box>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Total Loans
                </Typography>
                <Typography variant="h6">
                  {group.currency || 'RWF'} {parseFloat(financialSummary.total_loans || 0).toLocaleString()}
                </Typography>
              </Box>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Average Attendance
                </Typography>
                <Typography variant="h6">
                  {parseFloat(financialSummary.average_attendance || 0).toFixed(1)}%
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default GroupDetail;

