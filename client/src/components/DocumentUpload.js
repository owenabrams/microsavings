import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Button,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  LinearProgress,
  Paper,
  Chip,
  Alert,
  Avatar,
  Grid,
  Card,
  CardMedia,
  CardContent,
  CardActions,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  InsertDriveFile as FileIcon,
  Image as ImageIcon,
  PictureAsPdf as PdfIcon,
  VideoLibrary as VideoIcon,
  AudioFile as AudioIcon,
  FolderZip as ArchiveIcon,
  TableChart as SpreadsheetIcon,
  Description as DocumentIcon,
  Article as TextIcon,
} from '@mui/icons-material';

const DocumentUpload = ({
  onFilesSelected,
  maxFiles = 10,
  maxFileSize = 50 * 1024 * 1024, // 50MB
  acceptedTypes = '*',
  showPreview = true,
  disabled = false,
}) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState(null);
  const [filePreviews, setFilePreviews] = useState({});
  const fileInputRef = useRef(null);

  const getFileIcon = (file) => {
    const type = file.type;
    const filename = file.name || '';
    const ext = filename.split('.').pop()?.toLowerCase();

    // Images
    if (type.startsWith('image/')) {
      return <ImageIcon color="primary" />;
    }

    // PDFs
    if (type === 'application/pdf' || ext === 'pdf') {
      return <PdfIcon color="error" />;
    }

    // Videos
    if (type.startsWith('video/') || ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv'].includes(ext)) {
      return <VideoIcon color="secondary" />;
    }

    // Audio
    if (type.startsWith('audio/') || ['mp3', 'wav', 'ogg', 'flac'].includes(ext)) {
      return <AudioIcon color="info" />;
    }

    // Archives
    if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)) {
      return <ArchiveIcon color="warning" />;
    }

    // Spreadsheets
    if (['xls', 'xlsx', 'csv', 'ods'].includes(ext) ||
        type.includes('spreadsheet') ||
        type.includes('excel')) {
      return <SpreadsheetIcon color="success" />;
    }

    // Documents
    if (['doc', 'docx', 'odt', 'rtf'].includes(ext) ||
        type.includes('document') ||
        type.includes('word')) {
      return <DocumentIcon color="info" />;
    }

    // Text files
    if (type.startsWith('text/') || ['txt', 'md', 'log'].includes(ext)) {
      return <TextIcon color="action" />;
    }

    // Default
    return <FileIcon color="action" />;
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const validateFile = (file) => {
    if (file.size > maxFileSize) {
      return `File ${file.name} is too large. Maximum size is ${formatFileSize(maxFileSize)}`;
    }
    return null;
  };

  const generatePreview = (file) => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setFilePreviews(prev => ({
          ...prev,
          [file.name]: reader.result
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleFiles = (files) => {
    setError(null);
    const fileArray = Array.from(files);

    // Check max files
    if (selectedFiles.length + fileArray.length > maxFiles) {
      setError(`Maximum ${maxFiles} files allowed`);
      return;
    }

    // Validate each file
    for (const file of fileArray) {
      const validationError = validateFile(file);
      if (validationError) {
        setError(validationError);
        return;
      }
    }

    const newFiles = [...selectedFiles, ...fileArray];
    setSelectedFiles(newFiles);

    // Generate previews for images
    if (showPreview) {
      fileArray.forEach(file => generatePreview(file));
    }

    // Notify parent component
    if (onFilesSelected) {
      onFilesSelected(newFiles);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (disabled) return;
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  const removeFile = (index) => {
    const fileToRemove = selectedFiles[index];
    const newFiles = selectedFiles.filter((_, i) => i !== index);
    setSelectedFiles(newFiles);

    // Remove preview
    if (fileToRemove && filePreviews[fileToRemove.name]) {
      setFilePreviews(prev => {
        const newPreviews = { ...prev };
        delete newPreviews[fileToRemove.name];
        return newPreviews;
      });
    }

    // Notify parent component
    if (onFilesSelected) {
      onFilesSelected(newFiles);
    }
  };

  const clearAll = () => {
    setSelectedFiles([]);
    setFilePreviews({});
    setError(null);
    if (onFilesSelected) {
      onFilesSelected([]);
    }
  };

  return (
    <Box>
      {/* Drag and Drop Area */}
      <Paper
        elevation={dragActive ? 4 : 1}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        sx={{
          p: 3,
          textAlign: 'center',
          border: dragActive ? '2px dashed #1976d2' : '2px dashed #ccc',
          backgroundColor: dragActive ? '#e3f2fd' : disabled ? '#f5f5f5' : '#fafafa',
          cursor: disabled ? 'not-allowed' : 'pointer',
          transition: 'all 0.3s ease',
          '&:hover': disabled ? {} : {
            backgroundColor: '#f0f0f0',
            borderColor: '#1976d2',
          },
        }}
        onClick={disabled ? undefined : handleButtonClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={acceptedTypes}
          onChange={handleChange}
          style={{ display: 'none' }}
          disabled={disabled}
        />
        
        <UploadIcon sx={{ fontSize: 48, color: disabled ? '#ccc' : '#1976d2', mb: 1 }} />
        
        <Typography variant="h6" gutterBottom>
          {dragActive ? 'Drop files here' : 'Drag & drop files here'}
        </Typography>
        
        <Typography variant="body2" color="textSecondary" gutterBottom>
          or
        </Typography>
        
        <Button
          variant="contained"
          component="span"
          disabled={disabled}
          sx={{ mt: 1 }}
        >
          Browse Files
        </Button>
        
        <Typography variant="caption" display="block" sx={{ mt: 2 }} color="textSecondary">
          Maximum {maxFiles} files, up to {formatFileSize(maxFileSize)} each
        </Typography>
      </Paper>

      {/* Error Message */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Selected Files List */}
      {selectedFiles.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="subtitle2">
              Selected Files ({selectedFiles.length})
            </Typography>
            <Button size="small" onClick={clearAll} color="error">
              Clear All
            </Button>
          </Box>

          {showPreview ? (
            // Grid view with previews
            <Grid container spacing={2}>
              {selectedFiles.map((file, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Card variant="outlined">
                    {filePreviews[file.name] ? (
                      <CardMedia
                        component="img"
                        height="140"
                        image={filePreviews[file.name]}
                        alt={file.name}
                        sx={{ objectFit: 'cover' }}
                      />
                    ) : (
                      <Box
                        sx={{
                          height: 140,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          bgcolor: 'grey.100'
                        }}
                      >
                        {getFileIcon(file)}
                      </Box>
                    )}
                    <CardContent sx={{ pb: 1 }}>
                      <Typography variant="body2" noWrap title={file.name}>
                        {file.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {formatFileSize(file.size)}
                      </Typography>
                    </CardContent>
                    <CardActions sx={{ pt: 0 }}>
                      <IconButton
                        size="small"
                        onClick={() => removeFile(index)}
                        color="error"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            // List view without previews
            <Paper variant="outlined">
              <List dense>
                {selectedFiles.map((file, index) => (
                  <ListItem key={index}>
                    {filePreviews[file.name] ? (
                      <Avatar
                        src={filePreviews[file.name]}
                        variant="rounded"
                        sx={{ width: 40, height: 40, mr: 2 }}
                      >
                        {getFileIcon(file)}
                      </Avatar>
                    ) : (
                      getFileIcon(file)
                    )}
                    <ListItemText
                      primary={file.name}
                      secondary={formatFileSize(file.size)}
                      sx={{ ml: filePreviews[file.name] ? 0 : 2 }}
                    />
                    <ListItemSecondaryAction>
                      <IconButton
                        edge="end"
                        aria-label="delete"
                        onClick={() => removeFile(index)}
                        size="small"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </Paper>
          )}
        </Box>
      )}
    </Box>
  );
};

export default DocumentUpload;

