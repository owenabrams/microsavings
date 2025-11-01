import React, { useState } from 'react';
import {
  Box,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Paper,
  Chip,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  CircularProgress,
  Avatar,
} from '@mui/material';
import {
  InsertDriveFile as FileIcon,
  Image as ImageIcon,
  PictureAsPdf as PdfIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Description as DocumentIcon,
  VideoLibrary as VideoIcon,
  AudioFile as AudioIcon,
  FolderZip as ArchiveIcon,
  TableChart as SpreadsheetIcon,
  Article as TextIcon,
} from '@mui/icons-material';
import { transactionDocumentsAPI } from '../services/api';
import DocumentPreview from './DocumentPreview';

const DocumentList = ({
  documents = [],
  onDocumentDeleted,
  showActions = true,
  compact = false,
}) => {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [downloading, setDownloading] = useState({});
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewDocument, setPreviewDocument] = useState(null);

  const getFileIcon = (document) => {
    const mimeType = document.mime_type || '';
    const filename = document.original_filename || '';
    const ext = filename.split('.').pop()?.toLowerCase();

    // Images
    if (mimeType.startsWith('image/')) {
      return <ImageIcon color="primary" />;
    }

    // PDFs
    if (mimeType === 'application/pdf' || ext === 'pdf') {
      return <PdfIcon color="error" />;
    }

    // Videos
    if (mimeType.startsWith('video/') || ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv'].includes(ext)) {
      return <VideoIcon color="secondary" />;
    }

    // Audio
    if (mimeType.startsWith('audio/') || ['mp3', 'wav', 'ogg', 'flac'].includes(ext)) {
      return <AudioIcon color="info" />;
    }

    // Archives
    if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)) {
      return <ArchiveIcon color="warning" />;
    }

    // Spreadsheets
    if (['xls', 'xlsx', 'csv', 'ods'].includes(ext) ||
        mimeType.includes('spreadsheet') ||
        mimeType.includes('excel')) {
      return <SpreadsheetIcon color="success" />;
    }

    // Documents
    if (['doc', 'docx', 'odt', 'rtf'].includes(ext) ||
        mimeType.includes('document') ||
        mimeType.includes('word')) {
      return <DocumentIcon color="info" />;
    }

    // Text files
    if (mimeType.startsWith('text/') || ['txt', 'md', 'log'].includes(ext)) {
      return <TextIcon color="action" />;
    }

    // Default
    return <FileIcon color="action" />;
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getDocumentTypeColor = (type) => {
    const colors = {
      'RECEIPT': 'success',
      'INVOICE': 'warning',
      'PHOTO': 'info',
      'REPORT': 'primary',
      'CERTIFICATE': 'secondary',
      'OTHER': 'default',
    };
    return colors[type] || 'default';
  };

  const handleDownload = async (document) => {
    setDownloading(prev => ({ ...prev, [document.id]: true }));
    
    try {
      const response = await transactionDocumentsAPI.downloadDocument(document.id);
      
      // Create blob and download
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = window.document.createElement('a');
      link.href = url;
      link.download = document.original_filename || document.document_name;
      window.document.body.appendChild(link);
      link.click();
      window.document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading document:', error);
      alert('Failed to download document');
    } finally {
      setDownloading(prev => ({ ...prev, [document.id]: false }));
    }
  };

  const handleDeleteClick = (document) => {
    setDocumentToDelete(document);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!documentToDelete) return;
    
    setDeleting(true);
    try {
      await transactionDocumentsAPI.deleteDocument(documentToDelete.id);
      
      // Notify parent component
      if (onDocumentDeleted) {
        onDocumentDeleted(documentToDelete.id);
      }
      
      setDeleteDialogOpen(false);
      setDocumentToDelete(null);
    } catch (error) {
      console.error('Error deleting document:', error);
      alert('Failed to delete document');
    } finally {
      setDeleting(false);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setDocumentToDelete(null);
  };

  const handlePreview = (document) => {
    setPreviewDocument(document);
    setPreviewOpen(true);
  };

  const handlePreviewClose = () => {
    setPreviewOpen(false);
    setPreviewDocument(null);
  };

  const getThumbnailUrl = (document) => {
    if (!document.has_preview) return null;
    const token = localStorage.getItem('token');
    return `${process.env.REACT_APP_API_URL || 'http://localhost:5001/api'}/transaction-documents/documents/${document.id}/preview?type=thumbnail&token=${token}`;
  };

  if (!documents || documents.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <DocumentIcon sx={{ fontSize: 48, color: '#ccc', mb: 1 }} />
        <Typography variant="body2" color="textSecondary">
          No documents attached
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Paper variant="outlined">
        <List dense={compact}>
          {documents.map((document) => (
            <ListItem key={document.id}>
              <ListItemIcon>
                {document.has_preview ? (
                  <Avatar
                    src={getThumbnailUrl(document)}
                    variant="rounded"
                    sx={{ width: 40, height: 40, cursor: 'pointer' }}
                    onClick={() => handlePreview(document)}
                  >
                    {getFileIcon(document)}
                  </Avatar>
                ) : (
                  getFileIcon(document)
                )}
              </ListItemIcon>

              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2" noWrap sx={{ maxWidth: compact ? 200 : 400 }}>
                      {document.original_filename || document.document_name}
                    </Typography>
                    {document.document_type && (
                      <Chip
                        label={document.document_type}
                        size="small"
                        color={getDocumentTypeColor(document.document_type)}
                      />
                    )}
                    {document.is_proof_document && (
                      <Chip label="Proof" size="small" color="success" variant="outlined" />
                    )}
                    {document.is_compressed && (
                      <Chip label="Compressed" size="small" variant="outlined" />
                    )}
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="caption" display="block">
                      {formatFileSize(document.file_size)}
                      {document.is_compressed && document.compressed_size && (
                        <> → {formatFileSize(document.compressed_size)} ({document.compression_ratio}% saved)</>
                      )}
                    </Typography>
                    {!compact && document.description && (
                      <Typography variant="caption" display="block" color="textSecondary">
                        {document.description}
                      </Typography>
                    )}
                    {!compact && (
                      <Typography variant="caption" display="block" color="textSecondary">
                        Uploaded {formatDate(document.upload_date)}
                      </Typography>
                    )}
                  </Box>
                }
              />
              
              {showActions && (
                <ListItemSecondaryAction>
                  <Tooltip title="View">
                    <IconButton
                      edge="end"
                      aria-label="view"
                      onClick={() => handlePreview(document)}
                      size="small"
                      sx={{ mr: 0.5 }}
                    >
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>

                  <Tooltip title="Download">
                    <IconButton
                      edge="end"
                      aria-label="download"
                      onClick={() => handleDownload(document)}
                      disabled={downloading[document.id]}
                      size="small"
                      sx={{ mr: 0.5 }}
                    >
                      {downloading[document.id] ? (
                        <CircularProgress size={20} />
                      ) : (
                        <DownloadIcon />
                      )}
                    </IconButton>
                  </Tooltip>

                  <Tooltip title="Delete">
                    <IconButton
                      edge="end"
                      aria-label="delete"
                      onClick={() => handleDeleteClick(document)}
                      size="small"
                      sx={{ ml: 1 }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </ListItemSecondaryAction>
              )}
            </ListItem>
          ))}
        </List>
      </Paper>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={handleDeleteCancel}>
        <DialogTitle>Delete Document</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{documentToDelete?.original_filename}"?
          </Typography>
          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} disabled={deleting}>
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
            disabled={deleting}
          >
            {deleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Document Preview Dialog */}
      <DocumentPreview
        open={previewOpen}
        onClose={handlePreviewClose}
        document={previewDocument}
      />
    </Box>
  );
};

export default DocumentList;

