import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  IconButton,
  Typography,
  CircularProgress,
  Chip,
  Stack,
  Alert,
  Slider,
} from '@mui/material';
import {
  Close as CloseIcon,
  Download as DownloadIcon,
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  RotateRight as RotateRightIcon,
  Fullscreen as FullscreenIcon,
  NavigateBefore as NavigateBeforeIcon,
  NavigateNext as NavigateNextIcon,
} from '@mui/icons-material';
import { Document, Page, pdfjs } from 'react-pdf';
import { transactionDocumentsAPI } from '../services/api';

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

/**
 * DocumentPreview Component
 * 
 * Displays document preview in a modal dialog with zoom, rotate, and download controls.
 * Supports images with thumbnail/preview, and shows document info for non-previewable files.
 * 
 * @param {Object} props
 * @param {boolean} props.open - Whether the dialog is open
 * @param {Function} props.onClose - Callback when dialog is closed
 * @param {Object} props.document - Document object with metadata
 * @param {number} props.document.id - Document ID
 * @param {string} props.document.original_filename - Original filename
 * @param {string} props.document.document_type - Document type
 * @param {string} props.document.mime_type - MIME type
 * @param {number} props.document.file_size - File size in bytes
 * @param {boolean} props.document.has_preview - Whether preview is available
 * @param {string} props.document.upload_date - Upload date
 */
const DocumentPreview = ({ open, onClose, document }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [zoom, setZoom] = useState(100);
  const [rotation, setRotation] = useState(0);
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);

  if (!document) return null;

  const isImage = document.mime_type?.startsWith('image/');
  const isPDF = document.mime_type === 'application/pdf';
  const isVideo = document.mime_type?.startsWith('video/');
  const hasPreview = document.has_preview;

  const handleDownload = async () => {
    try {
      setLoading(true);
      const response = await transactionDocumentsAPI.downloadDocument(document.id);
      
      // Create blob and download
      const blob = new Blob([response.data], { type: document.mime_type });
      const url = window.URL.createObjectURL(blob);
      const link = window.document.createElement('a');
      link.href = url;
      link.download = document.original_filename;
      window.document.body.appendChild(link);
      link.click();
      window.document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download document');
      console.error('Download error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 25, 200));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 25, 50));
  };

  const handleRotate = () => {
    setRotation(prev => (prev + 90) % 360);
  };

  const handleFullscreen = () => {
    const elem = window.document.getElementById('preview-image');
    if (elem) {
      if (elem.requestFullscreen) {
        elem.requestFullscreen();
      } else if (elem.webkitRequestFullscreen) {
        elem.webkitRequestFullscreen();
      } else if (elem.msRequestFullscreen) {
        elem.msRequestFullscreen();
      }
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getPreviewUrl = (type = 'thumbnail') => {
    const token = localStorage.getItem('token');
    return `${process.env.REACT_APP_API_URL || 'http://localhost:5001/api'}/transaction-documents/documents/${document.id}/preview?type=${type}&token=${token}`;
  };

  const getDocumentUrl = () => {
    const token = localStorage.getItem('token');
    return `${process.env.REACT_APP_API_URL || 'http://localhost:5001/api'}/transaction-documents/documents/${document.id}/download?token=${token}`;
  };

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
    setPageNumber(1);
    setLoading(false);
  };

  const onDocumentLoadError = (error) => {
    console.error('PDF load error:', error);
    setError('Failed to load PDF document');
    setLoading(false);
  };

  const handlePreviousPage = () => {
    setPageNumber(prev => Math.max(prev - 1, 1));
  };

  const handleNextPage = () => {
    setPageNumber(prev => Math.min(prev + 1, numPages || 1));
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: {
          minHeight: '80vh',
          maxHeight: '90vh',
        }
      }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h6" component="div">
              {document.original_filename}
            </Typography>
            <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
              <Chip label={document.document_type} size="small" color="primary" />
              <Chip label={formatFileSize(document.file_size)} size="small" />
              {document.is_compressed && (
                <Chip label="Compressed" size="small" color="success" />
              )}
            </Stack>
          </Box>
          <IconButton onClick={onClose} edge="end">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        {loading && (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
            <Typography color="error">{error}</Typography>
          </Box>
        )}

        {!loading && !error && (
          <>
            {/* Image Preview */}
            {isImage && hasPreview && (
              <Box
                display="flex"
                justifyContent="center"
                alignItems="center"
                minHeight={400}
                sx={{ overflow: 'auto', bgcolor: 'grey.100', p: 2 }}
              >
                <img
                  id="preview-image"
                  src={getPreviewUrl('preview')}
                  alt={document.original_filename}
                  style={{
                    maxWidth: '100%',
                    maxHeight: '70vh',
                    transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
                    transition: 'transform 0.3s ease',
                  }}
                  onError={() => setError('Failed to load preview')}
                />
              </Box>
            )}

            {/* PDF Preview */}
            {isPDF && (
              <Box
                display="flex"
                flexDirection="column"
                alignItems="center"
                minHeight={400}
                sx={{ overflow: 'auto', bgcolor: 'grey.100', p: 2 }}
              >
                <Document
                  file={getDocumentUrl()}
                  onLoadSuccess={onDocumentLoadSuccess}
                  onLoadError={onDocumentLoadError}
                  loading={
                    <Box display="flex" justifyContent="center" p={4}>
                      <CircularProgress />
                    </Box>
                  }
                >
                  <Page
                    pageNumber={pageNumber}
                    scale={zoom / 100}
                    rotate={rotation}
                    renderTextLayer={true}
                    renderAnnotationLayer={true}
                  />
                </Document>

                {numPages && (
                  <Box mt={2} display="flex" alignItems="center" gap={2}>
                    <IconButton
                      onClick={handlePreviousPage}
                      disabled={pageNumber <= 1}
                      size="small"
                    >
                      <NavigateBeforeIcon />
                    </IconButton>
                    <Typography variant="body2">
                      Page {pageNumber} of {numPages}
                    </Typography>
                    <IconButton
                      onClick={handleNextPage}
                      disabled={pageNumber >= numPages}
                      size="small"
                    >
                      <NavigateNextIcon />
                    </IconButton>
                  </Box>
                )}
              </Box>
            )}

            {/* Video Preview */}
            {isVideo && (
              <Box
                display="flex"
                flexDirection="column"
                justifyContent="center"
                alignItems="center"
                minHeight={400}
                sx={{ bgcolor: 'grey.100', p: 2 }}
              >
                {hasPreview && (
                  <Box mb={2}>
                    <img
                      src={getPreviewUrl('thumbnail')}
                      alt={`${document.original_filename} thumbnail`}
                      style={{
                        maxWidth: '400px',
                        maxHeight: '300px',
                        borderRadius: '8px',
                      }}
                    />
                  </Box>
                )}
                <Alert severity="info" sx={{ mt: 2 }}>
                  Video playback not supported in preview. Download to view.
                </Alert>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2"><strong>Filename:</strong> {document.original_filename}</Typography>
                  <Typography variant="body2"><strong>Type:</strong> {document.mime_type}</Typography>
                  <Typography variant="body2"><strong>Size:</strong> {formatFileSize(document.file_size)}</Typography>
                </Box>
              </Box>
            )}

            {/* No Preview Available */}
            {!isImage && !isPDF && !isVideo && !hasPreview && (
              <Box
                display="flex"
                flexDirection="column"
                justifyContent="center"
                alignItems="center"
                minHeight={400}
                sx={{ bgcolor: 'grey.50', p: 4 }}
              >
                <Typography variant="h6" gutterBottom>
                  Preview not available
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  This file type doesn't support preview. Download to view.
                </Typography>
                <Box sx={{ mt: 3 }}>
                  <Typography variant="body2"><strong>Filename:</strong> {document.original_filename}</Typography>
                  <Typography variant="body2"><strong>Type:</strong> {document.mime_type}</Typography>
                  <Typography variant="body2"><strong>Size:</strong> {formatFileSize(document.file_size)}</Typography>
                  <Typography variant="body2"><strong>Uploaded:</strong> {formatDate(document.upload_date)}</Typography>
                  {document.description && (
                    <Typography variant="body2"><strong>Description:</strong> {document.description}</Typography>
                  )}
                </Box>
              </Box>
            )}
          </>
        )}
      </DialogContent>

      <DialogActions>
        {/* Zoom Controls (only for images/PDFs) */}
        {(isImage || isPDF) && (
          <Box sx={{ display: 'flex', gap: 1, mr: 'auto', alignItems: 'center' }}>
            <IconButton onClick={handleZoomOut} disabled={zoom <= 50} size="small" title="Zoom Out">
              <ZoomOutIcon />
            </IconButton>
            <Typography variant="body2" sx={{ minWidth: 50, textAlign: 'center' }}>
              {zoom}%
            </Typography>
            <IconButton onClick={handleZoomIn} disabled={zoom >= 200} size="small" title="Zoom In">
              <ZoomInIcon />
            </IconButton>
            <IconButton onClick={handleRotate} size="small" title="Rotate 90°">
              <RotateRightIcon />
            </IconButton>
            {isImage && hasPreview && (
              <IconButton onClick={handleFullscreen} size="small" title="Fullscreen">
                <FullscreenIcon />
              </IconButton>
            )}
          </Box>
        )}

        <Button
          startIcon={<DownloadIcon />}
          onClick={handleDownload}
          disabled={loading}
          variant="contained"
        >
          Download
        </Button>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentPreview;

