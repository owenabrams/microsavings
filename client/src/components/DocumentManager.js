import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Chip,
  CircularProgress,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Visibility as PreviewIcon,
  Close as CloseIcon,
  InsertDriveFile as FileIcon,
  Image as ImageIcon,
  PictureAsPdf as PdfIcon,
} from '@mui/icons-material';
import FileUpload from './FileUpload';
import { documentsAPI } from '../services/api';

const DocumentManager = ({ activityId, activityType, documents = [], readOnly = false }) => {
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [previewUrl, setPreviewUrl] = useState(null);
  const [previewDialogOpen, setPreviewDialogOpen] = useState(false);
  
  const queryClient = useQueryClient();

  // Get file icon based on file type
  const getFileIcon = (fileName) => {
    const ext = fileName.split('.').pop().toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(ext)) {
      return <ImageIcon color="primary" />;
    }
    if (ext === 'pdf') {
      return <PdfIcon color="error" />;
    }
    return <FileIcon />;
  };

  // Format file size
  const formatFileSize = (bytes) => {
    if (!bytes) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: async (files) => {
      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files', file);
      });
      return documentsAPI.uploadActivityDocuments(activityId, formData);
    },
    onSuccess: () => {
      setSnackbar({ open: true, message: 'Documents uploaded successfully', severity: 'success' });
      setUploadDialogOpen(false);
      setSelectedFiles([]);
      queryClient.invalidateQueries(['meeting']);
    },
    onError: (error) => {
      setSnackbar({ 
        open: true, 
        message: error.response?.data?.message || 'Failed to upload documents', 
        severity: 'error' 
      });
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (documentId) => documentsAPI.deleteDocument(documentId),
    onSuccess: () => {
      setSnackbar({ open: true, message: 'Document deleted successfully', severity: 'success' });
      queryClient.invalidateQueries(['meeting']);
    },
    onError: (error) => {
      setSnackbar({ 
        open: true, 
        message: error.response?.data?.message || 'Failed to delete document', 
        severity: 'error' 
      });
    },
  });

  // Handle upload
  const handleUpload = () => {
    if (selectedFiles.length === 0) {
      setSnackbar({ open: true, message: 'Please select files to upload', severity: 'warning' });
      return;
    }
    uploadMutation.mutate(selectedFiles);
  };

  // Handle download
  const handleDownload = async (documentId, fileName) => {
    try {
      const response = await documentsAPI.downloadDocument(documentId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setSnackbar({ 
        open: true, 
        message: 'Failed to download document', 
        severity: 'error' 
      });
    }
  };

  // Handle preview
  const handlePreview = async (documentId, fileName) => {
    try {
      const response = await documentsAPI.getDocumentPreview(documentId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      setPreviewUrl(url);
      setPreviewDialogOpen(true);
    } catch (error) {
      setSnackbar({ 
        open: true, 
        message: 'Preview not available for this file type', 
        severity: 'warning' 
      });
    }
  };

  // Handle delete
  const handleDelete = (documentId) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      deleteMutation.mutate(documentId);
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="subtitle1">
          Documents ({documents.length})
        </Typography>
        {!readOnly && (
          <Button
            variant="outlined"
            startIcon={<UploadIcon />}
            onClick={() => setUploadDialogOpen(true)}
            size="small"
          >
            Upload Documents
          </Button>
        )}
      </Box>

      {/* Documents List */}
      {documents.length === 0 ? (
        <Alert severity="info">No documents uploaded yet</Alert>
      ) : (
        <List>
          {documents.map((doc) => (
            <ListItem
              key={doc.id}
              sx={{
                border: '1px solid #e0e0e0',
                borderRadius: 1,
                mb: 1,
                backgroundColor: '#fafafa',
              }}
            >
              <Box sx={{ mr: 2 }}>
                {getFileIcon(doc.document_name || doc.file_name)}
              </Box>

              <ListItemText
                primary={doc.document_name || doc.file_name}
                secondary={
                  <Box>
                    <Typography variant="caption" display="block">
                      Size: {formatFileSize(doc.file_size)}
                    </Typography>
                    {doc.is_compressed && (
                      <Chip 
                        label={`Compressed (${doc.compression_ratio}% saved)`} 
                        size="small" 
                        color="success" 
                        sx={{ mt: 0.5 }}
                      />
                    )}
                  </Box>
                }
              />

              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  onClick={() => handlePreview(doc.id, doc.document_name || doc.file_name)}
                  title="Preview"
                  sx={{ mr: 1 }}
                >
                  <PreviewIcon />
                </IconButton>
                <IconButton
                  edge="end"
                  onClick={() => handleDownload(doc.id, doc.document_name || doc.file_name)}
                  title="Download"
                  sx={{ mr: 1 }}
                >
                  <DownloadIcon />
                </IconButton>
                {!readOnly && (
                  <IconButton
                    edge="end"
                    onClick={() => handleDelete(doc.id)}
                    color="error"
                    title="Delete"
                  >
                    <DeleteIcon />
                  </IconButton>
                )}
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      )}

      {/* Upload Dialog */}
      <Dialog
        open={uploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Upload Documents
          <IconButton
            onClick={() => setUploadDialogOpen(false)}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <FileUpload
            onFilesSelected={setSelectedFiles}
            maxFiles={10}
            disabled={uploadMutation.isPending}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleUpload}
            disabled={uploadMutation.isPending || selectedFiles.length === 0}
            startIcon={uploadMutation.isPending ? <CircularProgress size={20} /> : <UploadIcon />}
          >
            {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Preview Dialog */}
      <Dialog
        open={previewDialogOpen}
        onClose={() => {
          setPreviewDialogOpen(false);
          if (previewUrl) {
            window.URL.revokeObjectURL(previewUrl);
            setPreviewUrl(null);
          }
        }}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          Document Preview
          <IconButton
            onClick={() => {
              setPreviewDialogOpen(false);
              if (previewUrl) {
                window.URL.revokeObjectURL(previewUrl);
                setPreviewUrl(null);
              }
            }}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {previewUrl && (
            <Box
              component="img"
              src={previewUrl}
              alt="Preview"
              sx={{
                width: '100%',
                height: 'auto',
                maxHeight: '70vh',
                objectFit: 'contain',
              }}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Snackbar */}
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

export default DocumentManager;

