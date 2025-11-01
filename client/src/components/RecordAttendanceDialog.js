import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Checkbox,
  TextField,
  Box,
  Typography,
} from '@mui/material';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { meetingsAPI, groupsAPI } from '../services/api';

export default function RecordAttendanceDialog({ open, onClose, meetingId, groupId }) {
  const queryClient = useQueryClient();
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [error, setError] = useState(null);

  // Fetch group members
  const { data: membersData, isLoading: membersLoading } = useQuery({
    queryKey: ['groupMembers', groupId],
    queryFn: async () => {
      const response = await groupsAPI.getMembers(groupId);
      return response.data;
    },
    enabled: open && !!groupId,
  });

  // Fetch existing attendance records
  const { data: meetingData } = useQuery({
    queryKey: ['meeting', meetingId],
    queryFn: async () => {
      const response = await meetingsAPI.getMeetingDetail(meetingId);
      return response.data;
    },
    enabled: open && !!meetingId,
  });

  // Initialize attendance records when members data is loaded
  useEffect(() => {
    if (membersData?.data?.members) {
      const members = membersData.data.members;
      const existingAttendance = meetingData?.attendance || [];

      const records = members.map((member) => {
        const existing = existingAttendance.find((a) => a.member_id === member.id);
        return {
          member_id: member.id,
          member_name: `${member.first_name} ${member.last_name}`,
          is_present: existing?.is_present || false,
          arrival_time: existing?.arrival_time || '',
          excuse_reason: existing?.excuse_reason || '',
        };
      });

      setAttendanceRecords(records);
    }
  }, [membersData, meetingData]);

  const recordMutation = useMutation({
    mutationFn: async (data) => {
      const response = await meetingsAPI.recordAttendance(meetingId, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['meeting', meetingId]);
      queryClient.invalidateQueries(['meetings', groupId]);
      handleClose();
    },
    onError: (error) => {
      setError(error.response?.data?.message || 'Failed to record attendance');
    },
  });

  const handleTogglePresence = (memberId) => {
    setAttendanceRecords((prev) =>
      prev.map((record) =>
        record.member_id === memberId
          ? { ...record, is_present: !record.is_present }
          : record
      )
    );
  };

  const handleFieldChange = (memberId, field, value) => {
    setAttendanceRecords((prev) =>
      prev.map((record) =>
        record.member_id === memberId ? { ...record, [field]: value } : record
      )
    );
  };

  const handleSubmit = () => {
    const attendanceData = {
      attendance: attendanceRecords.map((record) => ({
        member_id: record.member_id,
        is_present: record.is_present,
        arrival_time: record.arrival_time || null,
        excuse_reason: record.excuse_reason || null,
      })),
    };

    recordMutation.mutate(attendanceData);
  };

  const handleClose = () => {
    setError(null);
    onClose();
  };

  const presentCount = attendanceRecords.filter((r) => r.is_present).length;
  const totalCount = attendanceRecords.length;

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Record Attendance</DialogTitle>
      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {membersLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body1">
                <strong>Present:</strong> {presentCount} / {totalCount} ({totalCount > 0 ? ((presentCount / totalCount) * 100).toFixed(1) : 0}%)
              </Typography>
            </Box>

            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell padding="checkbox">Present</TableCell>
                    <TableCell>Member Name</TableCell>
                    <TableCell>Arrival Time</TableCell>
                    <TableCell>Excuse/Reason</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {attendanceRecords.map((record) => (
                    <TableRow key={record.member_id}>
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={record.is_present}
                          onChange={() => handleTogglePresence(record.member_id)}
                        />
                      </TableCell>
                      <TableCell>{record.member_name}</TableCell>
                      <TableCell>
                        <TextField
                          type="time"
                          size="small"
                          value={record.arrival_time}
                          onChange={(e) =>
                            handleFieldChange(record.member_id, 'arrival_time', e.target.value)
                          }
                          disabled={!record.is_present}
                          InputLabelProps={{ shrink: true }}
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          size="small"
                          fullWidth
                          value={record.excuse_reason}
                          onChange={(e) =>
                            handleFieldChange(record.member_id, 'excuse_reason', e.target.value)
                          }
                          placeholder={record.is_present ? 'Notes' : 'Reason for absence'}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={recordMutation.isPending || membersLoading}
        >
          {recordMutation.isPending ? <CircularProgress size={24} /> : 'Save Attendance'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

