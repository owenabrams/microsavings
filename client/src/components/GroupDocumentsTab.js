import React, { useState } from 'react';
import {
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Chip,
  CircularProgress,
  Paper,
  Divider,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Upload as UploadIcon,
  Visibility as VisibilityIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Description as DescriptionIcon,
  PictureAsPdf as PdfIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { groupDocumentsAPI } from '../services/api';

const DOCUMENT_TYPES = {
  CONSTITUTION: {
    label: 'Constitution Documents',
    description: 'Group constitution, bylaws, and amendments',
    color: 'primary',
  },
  FINANCIAL_RECORD: {
    label: 'Financial Documents',
    description: 'Financial reports, audits, and records',
    color: 'success',
  },
  REGISTRATION: {
    label: 'Registration Documents',
    description: 'Registration certificates and official documents',
    color: 'warning',
  },
};

function GroupDocumentsTab({ groupId, isAdmin = false }) {
  const queryClient = useQueryClient();
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [selectedDocumentType, setSelectedDocumentType] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [description, setDescription] = useState('');
  const [version, setVersion] = useState('1.0');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // Fetch all group documents
  const { data: documentsData, isLoading, error } = useQuery({
    queryKey: ['groupDocuments', groupId],
    queryFn: async () => {
      const response = await groupDocumentsAPI.getAll(groupId);
      return response.data.data;
    },
    enabled: !!groupId,
  });

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: async ({ files, documentType, metadata }) => {
      return await groupDocumentsAPI.upload(groupId, files, documentType, metadata);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['groupDocuments', groupId]);
      setUploadDialogOpen(false);
      setSelectedFiles([]);
      setDescription('');
      setVersion('1.0');
      setSnackbar({
        open: true,
        message: 'Documents uploaded successfully',
        severity: 'success',
      });
    },
    onError: (error) => {
      setSnackbar({
        open: true,
        message: error.response?.data?.message || 'Failed to upload documents',
        severity: 'error',
      });
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (documentId) => {
      return await groupDocumentsAPI.delete(groupId, documentId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['groupDocuments', groupId]);
      setDeleteDialogOpen(false);
      setDocumentToDelete(null);
      setSnackbar({
        open: true,
        message: 'Document deleted successfully',
        severity: 'success',
      });
    },
    onError: (error) => {
      setSnackbar({
        open: true,
        message: error.response?.data?.message || 'Failed to delete document',
        severity: 'error',
      });
    },
  });

  const handleUploadClick = (documentType) => {
    setSelectedDocumentType(documentType);
    setUploadDialogOpen(true);
  };

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files);
    // Validate PDF only
    const pdfFiles = files.filter(file => file.type === 'application/pdf');
    if (pdfFiles.length !== files.length) {
      setSnackbar({
        open: true,
        message: 'Only PDF files are allowed',
        severity: 'warning',
      });
    }
    setSelectedFiles(pdfFiles);
  };

  const handleUpload = () => {
    if (selectedFiles.length === 0) {
      setSnackbar({
        open: true,
        message: 'Please select at least one file',
        severity: 'warning',
      });
      return;
    }

    uploadMutation.mutate({
      files: selectedFiles,
      documentType: selectedDocumentType,
      metadata: { description, version },
    });
  };

  const handleDownload = async (document) => {
    try {
      const response = await groupDocumentsAPI.download(groupId, document.id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', document.file_name);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Failed to download document',
        severity: 'error',
      });
    }
  };

  const handlePreview = async (document) => {
    try {
      const response = await groupDocumentsAPI.preview(groupId, document.id);
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      window.open(url, '_blank');
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Failed to preview document',
        severity: 'error',
      });
    }
  };

  const handleDeleteClick = (document) => {
    setDocumentToDelete(document);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (documentToDelete) {
      deleteMutation.mutate(documentToDelete.id);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'Unknown';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getDocumentsByType = (type) => {
    if (!documentsData) return [];
    return documentsData.filter(doc => doc.document_type === type);
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load documents: {error.message}
      </Alert>
    );
  }

  return (
    <Box>
      {!isAdmin && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Only group admins and leaders can upload or delete documents.
        </Alert>
      )}

      {snackbar.open && (
        <Alert
          severity={snackbar.severity}
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          sx={{ mb: 2 }}
        >
          {snackbar.message}
        </Alert>
      )}

      {Object.entries(DOCUMENT_TYPES).map(([type, config]) => {
        const documents = getDocumentsByType(type);
        
        return (
          <Accordion key={type} defaultExpanded={type === 'CONSTITUTION'}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box display="flex" alignItems="center" gap={2} width="100%">
                <DescriptionIcon color={config.color} />
                <Box flex={1}>
                  <Typography variant="h6">{config.label}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {config.description}
                  </Typography>
                </Box>
                <Chip
                  label={`${documents.length} document${documents.length !== 1 ? 's' : ''}`}
                  color={config.color}
                  size="small"
                />
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Box>
                {isAdmin && (
                  <Button
                    variant="contained"
                    startIcon={<UploadIcon />}
                    onClick={() => handleUploadClick(type)}
                    sx={{ mb: 2 }}
                    color={config.color}
                  >
                    Upload Documents
                  </Button>
                )}

                {documents.length === 0 ? (
                  <Paper sx={{ p: 3, textAlign: 'center', bgcolor: 'grey.50' }}>
                    <DescriptionIcon sx={{ fontSize: 48, color: 'grey.400', mb: 1 }} />
                    <Typography color="text.secondary">
                      No documents uploaded yet
                    </Typography>
                  </Paper>
                ) : (
                  <List>
                    {documents.map((doc, index) => (
                      <React.Fragment key={doc.id}>
                        {index > 0 && <Divider />}
                        <ListItem>
                          <PdfIcon sx={{ mr: 2, color: 'error.main' }} />
                          <ListItemText
                            primary={
                              <Box display="flex" alignItems="center" gap={1}>
                                <Typography variant="subtitle1">
                                  {doc.document_title}
                                </Typography>
                                {doc.is_compressed && (
                                  <Chip
                                    label={`Compressed ${doc.compression_ratio}%`}
                                    size="small"
                                    color="success"
                                    variant="outlined"
                                  />
                                )}
                              </Box>
                            }
                            secondary={
                              <Box>
                                <Typography variant="body2" color="text.secondary">
                                  {formatFileSize(doc.file_size)} • Uploaded by {doc.uploaded_by} • {formatDate(doc.upload_date)}
                                </Typography>
                                {doc.description && (
                                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                                    {doc.description}
                                  </Typography>
                                )}
                              </Box>
                            }
                          />
                          <ListItemSecondaryAction>
                            <Tooltip title="Preview">
                              <IconButton
                                edge="end"
                                onClick={() => handlePreview(doc)}
                                sx={{ mr: 1 }}
                              >
                                <VisibilityIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Download">
                              <IconButton
                                edge="end"
                                onClick={() => handleDownload(doc)}
                                sx={{ mr: 1 }}
                              >
                                <DownloadIcon />
                              </IconButton>
                            </Tooltip>
                            {isAdmin && (
                              <Tooltip title="Delete">
                                <IconButton
                                  edge="end"
                                  onClick={() => handleDeleteClick(doc)}
                                  color="error"
                                >
                                  <DeleteIcon />
                                </IconButton>
                              </Tooltip>
                            )}
                          </ListItemSecondaryAction>
                        </ListItem>
                      </React.Fragment>
                    ))}
                  </List>
                )}
              </Box>
            </AccordionDetails>
          </Accordion>
        );
      })}

      {/* Upload Dialog */}
      <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Upload {selectedDocumentType && DOCUMENT_TYPES[selectedDocumentType]?.label}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Alert severity="info" sx={{ mb: 2 }}>
              Only PDF files are allowed. Maximum file size: 50MB per file.
            </Alert>
            
            <input
              type="file"
              accept="application/pdf"
              multiple
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              id="file-upload"
            />
            <label htmlFor="file-upload">
              <Button
                variant="outlined"
                component="span"
                startIcon={<UploadIcon />}
                fullWidth
                sx={{ mb: 2 }}
              >
                Select PDF Files
              </Button>
            </label>

            {selectedFiles.length > 0 && (
              <Paper sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
                <Typography variant="subtitle2" gutterBottom>
                  Selected Files ({selectedFiles.length}):
                </Typography>
                {selectedFiles.map((file, index) => (
                  <Typography key={index} variant="body2" color="text.secondary">
                    • {file.name} ({formatFileSize(file.size)})
                  </Typography>
                ))}
              </Paper>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleUpload}
            variant="contained"
            disabled={selectedFiles.length === 0 || uploadMutation.isPending}
          >
            {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Document</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{documentToDelete?.document_title}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default GroupDocumentsTab;

