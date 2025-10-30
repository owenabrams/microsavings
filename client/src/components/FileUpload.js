import React, { useState, useCallback } from 'react';
import {
  Box,
  Button,
  IconButton,
  Typography,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Paper,
  Chip,
  Alert,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  InsertDriveFile as FileIcon,
  Image as ImageIcon,
  PictureAsPdf as PdfIcon,
  VideoLibrary as VideoIcon,
  AudioFile as AudioIcon,
  Folder as FolderIcon,
} from '@mui/icons-material';

const FileUpload = ({ 
  onFilesSelected, 
  maxFiles = 10, 
  maxFileSize = 50 * 1024 * 1024, // 50MB
  acceptedFileTypes = null, // null means all types
  disabled = false,
  showPreview = true,
}) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState('');

  // Get file icon based on file type
  const getFileIcon = (file) => {
    const type = file.type;
    if (type.startsWith('image/')) return <ImageIcon color="primary" />;
    if (type === 'application/pdf') return <PdfIcon color="error" />;
    if (type.startsWith('video/')) return <VideoIcon color="secondary" />;
    if (type.startsWith('audio/')) return <AudioIcon color="info" />;
    if (type.includes('zip') || type.includes('rar') || type.includes('tar')) 
      return <FolderIcon color="warning" />;
    return <FileIcon />;
  };

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  // Validate file
  const validateFile = (file) => {
    // Check file size
    if (file.size > maxFileSize) {
      return `File "${file.name}" exceeds maximum size of ${formatFileSize(maxFileSize)}`;
    }

    // Check file type if specified
    if (acceptedFileTypes && acceptedFileTypes.length > 0) {
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
      const mimeType = file.type;
      
      const isAccepted = acceptedFileTypes.some(type => {
        if (type.startsWith('.')) {
          return fileExtension === type.toLowerCase();
        }
        if (type.includes('/*')) {
          const category = type.split('/')[0];
          return mimeType.startsWith(category + '/');
        }
        return mimeType === type;
      });

      if (!isAccepted) {
        return `File type "${fileExtension}" is not accepted`;
      }
    }

    return null;
  };

  // Handle file selection
  const handleFiles = useCallback((files) => {
    setError('');
    const fileArray = Array.from(files);

    // Check max files limit
    if (selectedFiles.length + fileArray.length > maxFiles) {
      setError(`Maximum ${maxFiles} files allowed`);
      return;
    }

    // Validate each file
    const validFiles = [];
    for (const file of fileArray) {
      const validationError = validateFile(file);
      if (validationError) {
        setError(validationError);
        return;
      }
      validFiles.push(file);
    }

    // Add files with preview URLs for images
    const filesWithPreviews = validFiles.map(file => ({
      file,
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : null,
      id: Math.random().toString(36).substr(2, 9),
    }));

    const newFiles = [...selectedFiles, ...filesWithPreviews];
    setSelectedFiles(newFiles);
    
    // Notify parent component
    if (onFilesSelected) {
      onFilesSelected(newFiles.map(f => f.file));
    }
  }, [selectedFiles, maxFiles, onFilesSelected]);

  // Handle drag events
  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  // Handle drop
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  }, [disabled, handleFiles]);

  // Handle file input change
  const handleChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
    }
  };

  // Remove file
  const removeFile = (fileId) => {
    const newFiles = selectedFiles.filter(f => f.id !== fileId);
    setSelectedFiles(newFiles);
    
    // Revoke preview URL to free memory
    const removedFile = selectedFiles.find(f => f.id === fileId);
    if (removedFile?.preview) {
      URL.revokeObjectURL(removedFile.preview);
    }

    // Notify parent component
    if (onFilesSelected) {
      onFilesSelected(newFiles.map(f => f.file));
    }
  };

  // Clear all files
  const clearAll = () => {
    selectedFiles.forEach(f => {
      if (f.preview) URL.revokeObjectURL(f.preview);
    });
    setSelectedFiles([]);
    if (onFilesSelected) {
      onFilesSelected([]);
    }
  };

  return (
    <Box>
      {/* Drop Zone */}
      <Paper
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        sx={{
          border: dragActive ? '2px dashed #1976d2' : '2px dashed #ccc',
          borderRadius: 2,
          p: 3,
          textAlign: 'center',
          backgroundColor: dragActive ? 'rgba(25, 118, 210, 0.05)' : 'transparent',
          cursor: disabled ? 'not-allowed' : 'pointer',
          opacity: disabled ? 0.6 : 1,
          transition: 'all 0.3s ease',
        }}
      >
        <input
          type="file"
          id="file-upload-input"
          multiple
          onChange={handleChange}
          disabled={disabled}
          accept={acceptedFileTypes ? acceptedFileTypes.join(',') : undefined}
          style={{ display: 'none' }}
        />
        
        <label htmlFor="file-upload-input" style={{ cursor: disabled ? 'not-allowed' : 'pointer' }}>
          <UploadIcon sx={{ fontSize: 48, color: dragActive ? 'primary.main' : 'text.secondary', mb: 1 }} />
          <Typography variant="h6" gutterBottom>
            {dragActive ? 'Drop files here' : 'Drag & drop files here'}
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            or
          </Typography>
          <Button
            variant="contained"
            component="span"
            disabled={disabled}
            startIcon={<UploadIcon />}
            sx={{ mt: 1 }}
          >
            Browse Files
          </Button>
          <Typography variant="caption" display="block" sx={{ mt: 2 }} color="text.secondary">
            Maximum {maxFiles} files, up to {formatFileSize(maxFileSize)} each
          </Typography>
        </label>
      </Paper>

      {/* Error Message */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Selected Files List */}
      {selectedFiles.length > 0 && (
        <Box sx={{ mt: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="subtitle1">
              Selected Files ({selectedFiles.length})
            </Typography>
            <Button size="small" onClick={clearAll} color="error">
              Clear All
            </Button>
          </Box>

          <List>
            {selectedFiles.map((fileObj) => (
              <ListItem
                key={fileObj.id}
                sx={{
                  border: '1px solid #e0e0e0',
                  borderRadius: 1,
                  mb: 1,
                  backgroundColor: '#fafafa',
                }}
              >
                <Box sx={{ mr: 2 }}>
                  {getFileIcon(fileObj.file)}
                </Box>
                
                {showPreview && fileObj.preview && (
                  <Box
                    component="img"
                    src={fileObj.preview}
                    alt={fileObj.file.name}
                    sx={{
                      width: 50,
                      height: 50,
                      objectFit: 'cover',
                      borderRadius: 1,
                      mr: 2,
                    }}
                  />
                )}

                <ListItemText
                  primary={fileObj.file.name}
                  secondary={formatFileSize(fileObj.file.size)}
                />

                <ListItemSecondaryAction>
                  <IconButton
                    edge="end"
                    onClick={() => removeFile(fileObj.id)}
                    color="error"
                  >
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </Box>
      )}
    </Box>
  );
};

export default FileUpload;

