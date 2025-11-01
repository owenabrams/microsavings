"""
Professional File Storage Service
Handles file upload, compression, preview generation, and storage management.
"""
import os
import uuid
import shutil
import datetime
import hashlib
import gzip
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import Image
import PyPDF2
from werkzeug.utils import secure_filename
from flask import current_app

# Optional imports for advanced features
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False


class FileStorageService:
    """
    Comprehensive file storage service with:
    - Upload/download management
    - Automatic compression for large files
    - Preview/thumbnail generation
    - Storage quota tracking
    - File versioning
    - Cascading deletes
    """
    
    # File size thresholds
    COMPRESSION_THRESHOLD = 5 * 1024 * 1024  # 5MB - compress files larger than this
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Preview settings
    THUMBNAIL_SIZE = (300, 300)
    PREVIEW_SIZE = (800, 600)
    PDF_PREVIEW_DPI = 150
    
    # Allowed extensions
    ALLOWED_EXTENSIONS = {
        'documents': {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'csv', 'odt', 'ods'},
        'images': {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'},
        'videos': {'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv'},
        'archives': {'zip', 'rar', '7z', 'tar', 'gz'},
        'audio': {'mp3', 'wav', 'ogg', 'flac'}
    }
    
    # MIME types
    MIME_TYPES = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'txt': 'text/plain',
        'csv': 'text/csv',
        'odt': 'application/vnd.oasis.opendocument.text',
        'ods': 'application/vnd.oasis.opendocument.spreadsheet',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'bmp': 'image/bmp',
        'webp': 'image/webp',
        'svg': 'image/svg+xml',
        'mp4': 'video/mp4',
        'avi': 'video/x-msvideo',
        'mov': 'video/quicktime',
        'wmv': 'video/x-ms-wmv',
        'flv': 'video/x-flv',
        'mkv': 'video/x-matroska',
        'zip': 'application/zip',
        'rar': 'application/x-rar-compressed',
        '7z': 'application/x-7z-compressed',
        'tar': 'application/x-tar',
        'gz': 'application/gzip',
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
        'ogg': 'audio/ogg',
        'flac': 'audio/flac'
    }
    
    def __init__(self, base_upload_folder: str = None):
        """Initialize file storage service."""
        self.base_upload_folder = base_upload_folder or current_app.config.get('UPLOAD_FOLDER', '/app/uploads')
        self._ensure_base_directories()
    
    def _ensure_base_directories(self):
        """Ensure base upload directories exist."""
        directories = [
            self.base_upload_folder,
            os.path.join(self.base_upload_folder, 'activities'),
            os.path.join(self.base_upload_folder, 'groups'),
            os.path.join(self.base_upload_folder, 'members'),
            os.path.join(self.base_upload_folder, 'meetings'),
            os.path.join(self.base_upload_folder, 'previews'),
            os.path.join(self.base_upload_folder, 'thumbnails'),
            os.path.join(self.base_upload_folder, 'temp')
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Extract file extension from filename."""
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    @staticmethod
    def get_file_category(extension: str) -> str:
        """Determine file category from extension."""
        for category, extensions in FileStorageService.ALLOWED_EXTENSIONS.items():
            if extension in extensions:
                return category
        return 'other'
    
    @staticmethod
    def get_mime_type(filename: str, file_path: str = None) -> str:
        """
        Get MIME type from filename extension or file content.

        Args:
            filename: Name of the file
            file_path: Optional path to file for content-based detection

        Returns:
            MIME type string
        """
        # Try content-based detection first if file path provided
        if file_path and MAGIC_AVAILABLE and os.path.exists(file_path):
            try:
                mime = magic.Magic(mime=True)
                return mime.from_file(file_path)
            except Exception:
                pass

        # Fall back to extension-based detection
        ext = FileStorageService.get_file_extension(filename)
        return FileStorageService.MIME_TYPES.get(ext, 'application/octet-stream')
    
    @staticmethod
    def is_allowed_file(filename: str) -> bool:
        """Check if file extension is allowed."""
        ext = FileStorageService.get_file_extension(filename)
        all_extensions = set()
        for extensions in FileStorageService.ALLOWED_EXTENSIONS.values():
            all_extensions.update(extensions)
        return ext in all_extensions
    
    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """Calculate SHA256 hash of file for duplicate detection."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def get_storage_path(self, entity_type: str, entity_id: int, filename: str = None) -> str:
        """
        Get storage path for entity.
        
        Args:
            entity_type: Type of entity (activity, group, member, meeting)
            entity_id: ID of entity
            filename: Optional filename to append
        
        Returns:
            Full path to storage location
        """
        base_path = os.path.join(self.base_upload_folder, f"{entity_type}s", str(entity_id))
        os.makedirs(base_path, exist_ok=True)
        
        if filename:
            return os.path.join(base_path, filename)
        return base_path
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """Generate unique filename while preserving extension."""
        secure_name = secure_filename(original_filename)
        extension = self.get_file_extension(secure_name)
        unique_name = f"{uuid.uuid4().hex}.{extension}"
        return unique_name
    
    def compress_file(self, file_path: str, compression_level: int = 6) -> Tuple[str, int, int]:
        """
        Compress file using gzip.
        
        Args:
            file_path: Path to file to compress
            compression_level: Compression level (1-9, default 6)
        
        Returns:
            Tuple of (compressed_file_path, original_size, compressed_size)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        original_size = os.path.getsize(file_path)
        
        # Don't compress already compressed files
        ext = self.get_file_extension(file_path)
        if ext in {'zip', 'rar', '7z', 'gz', 'jpg', 'jpeg', 'png', 'mp4', 'mp3'}:
            return file_path, original_size, original_size
        
        compressed_path = f"{file_path}.gz"
        
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb', compresslevel=compression_level) as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        compressed_size = os.path.getsize(compressed_path)
        
        # Only keep compressed version if it's actually smaller
        if compressed_size < original_size * 0.9:  # At least 10% reduction
            os.remove(file_path)
            return compressed_path, original_size, compressed_size
        else:
            os.remove(compressed_path)
            return file_path, original_size, original_size
    
    def decompress_file(self, compressed_path: str, output_path: str = None) -> str:
        """
        Decompress gzipped file.
        
        Args:
            compressed_path: Path to compressed file
            output_path: Optional output path (defaults to removing .gz extension)
        
        Returns:
            Path to decompressed file
        """
        if not compressed_path.endswith('.gz'):
            return compressed_path
        
        if output_path is None:
            output_path = compressed_path[:-3]  # Remove .gz extension
        
        with gzip.open(compressed_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return output_path

    def generate_image_thumbnail(self, image_path: str, size: Tuple[int, int] = None) -> Optional[str]:
        """
        Generate thumbnail for image file.

        Args:
            image_path: Path to image file
            size: Thumbnail size (width, height), defaults to THUMBNAIL_SIZE

        Returns:
            Path to thumbnail file or None if generation failed
        """
        if size is None:
            size = self.THUMBNAIL_SIZE

        try:
            with Image.open(image_path) as img:
                # Convert RGBA to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background

                # Generate thumbnail
                img.thumbnail(size, Image.Resampling.LANCZOS)

                # Save thumbnail
                thumbnail_dir = os.path.join(self.base_upload_folder, 'thumbnails')
                os.makedirs(thumbnail_dir, exist_ok=True)

                filename = os.path.basename(image_path)
                thumbnail_filename = f"thumb_{filename}"
                thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)

                img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)

                return thumbnail_path

        except Exception as e:
            current_app.logger.error(f"Failed to generate thumbnail for {image_path}: {str(e)}")
            return None

    def generate_pdf_preview(self, pdf_path: str, page_number: int = 0) -> Optional[str]:
        """
        Generate preview image for PDF first page.

        Args:
            pdf_path: Path to PDF file
            page_number: Page number to preview (default: 0 = first page)

        Returns:
            Path to preview image or None if generation failed
        """
        if not PDF2IMAGE_AVAILABLE:
            current_app.logger.warning("pdf2image not available, skipping PDF preview generation")
            return None

        try:
            preview_dir = os.path.join(self.base_upload_folder, 'previews')
            os.makedirs(preview_dir, exist_ok=True)

            # Convert PDF page to image
            images = convert_from_path(
                pdf_path,
                first_page=page_number + 1,
                last_page=page_number + 1,
                dpi=self.PDF_PREVIEW_DPI
            )

            if images:
                # Save preview image
                filename = os.path.basename(pdf_path)
                preview_filename = f"preview_{os.path.splitext(filename)[0]}.jpg"
                preview_path = os.path.join(preview_dir, preview_filename)

                # Resize to preview size
                img = images[0]
                img.thumbnail(self.PREVIEW_SIZE, Image.Resampling.LANCZOS)
                img.save(preview_path, 'JPEG', quality=85, optimize=True)

                current_app.logger.info(f"Generated PDF preview: {preview_path}")
                return preview_path

            return None

        except Exception as e:
            current_app.logger.error(f"Failed to generate PDF preview for {pdf_path}: {str(e)}")
            return None

    def generate_video_thumbnail(self, video_path: str, time_offset: float = 1.0) -> Optional[str]:
        """
        Generate thumbnail from video file.

        Args:
            video_path: Path to video file
            time_offset: Time offset in seconds to capture frame (default: 1.0)

        Returns:
            Path to thumbnail image or None if generation failed
        """
        if not MOVIEPY_AVAILABLE:
            current_app.logger.warning("moviepy not available, skipping video thumbnail generation")
            return None

        try:
            thumbnail_dir = os.path.join(self.base_upload_folder, 'thumbnails')
            os.makedirs(thumbnail_dir, exist_ok=True)

            # Load video and extract frame
            with VideoFileClip(video_path) as video:
                # Use time_offset or 10% of video duration, whichever is smaller
                capture_time = min(time_offset, video.duration * 0.1)

                # Extract frame
                frame = video.get_frame(capture_time)

                # Convert to PIL Image
                img = Image.fromarray(frame)

                # Generate thumbnail
                img.thumbnail(self.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

                # Save thumbnail
                filename = os.path.basename(video_path)
                thumbnail_filename = f"thumb_{os.path.splitext(filename)[0]}.jpg"
                thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)

                img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)

                current_app.logger.info(f"Generated video thumbnail: {thumbnail_path}")
                return thumbnail_path

        except Exception as e:
            current_app.logger.error(f"Failed to generate video thumbnail for {video_path}: {str(e)}")
            return None

    def extract_file_metadata(self, file_path: str) -> Dict:
        """
        Extract metadata from file.

        Args:
            file_path: Path to file

        Returns:
            Dictionary containing file metadata
        """
        metadata = {
            'file_name': os.path.basename(file_path),
            'file_size': os.path.getsize(file_path),
            'file_extension': self.get_file_extension(file_path),
            'mime_type': self.get_mime_type(file_path),
            'file_category': self.get_file_category(self.get_file_extension(file_path)),
            'created_date': datetime.datetime.fromtimestamp(os.path.getctime(file_path)),
            'modified_date': datetime.datetime.fromtimestamp(os.path.getmtime(file_path)),
            'is_compressed': file_path.endswith('.gz'),
            'file_hash': self.calculate_file_hash(file_path)
        }

        # Add image-specific metadata
        ext = metadata['file_extension']
        if ext in self.ALLOWED_EXTENSIONS['images'] and ext != 'svg':
            try:
                with Image.open(file_path) as img:
                    metadata['image_width'] = img.width
                    metadata['image_height'] = img.height
                    metadata['image_format'] = img.format
                    metadata['image_mode'] = img.mode
            except Exception:
                pass

        # Add PDF-specific metadata
        if ext == 'pdf':
            try:
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    metadata['pdf_pages'] = len(pdf_reader.pages)
                    if pdf_reader.metadata:
                        metadata['pdf_title'] = pdf_reader.metadata.get('/Title', '')
                        metadata['pdf_author'] = pdf_reader.metadata.get('/Author', '')
                        metadata['pdf_subject'] = pdf_reader.metadata.get('/Subject', '')
            except Exception:
                pass

        return metadata

    def save_uploaded_file(self, file, entity_type: str, entity_id: int,
                          auto_compress: bool = True, generate_preview: bool = True) -> Dict:
        """
        Save uploaded file with optional compression and preview generation.

        Args:
            file: File object from request.files
            entity_type: Type of entity (activity, group, member, meeting)
            entity_id: ID of entity
            auto_compress: Whether to automatically compress large files
            generate_preview: Whether to generate preview/thumbnail

        Returns:
            Dictionary containing file information
        """
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        unique_filename = self.generate_unique_filename(original_filename)

        # Get storage path
        file_path = self.get_storage_path(entity_type, entity_id, unique_filename)

        # Save file
        file.save(file_path)

        # Get file size
        file_size = os.path.getsize(file_path)

        # Compress if needed
        compressed_size = file_size
        is_compressed = False
        if auto_compress and file_size > self.COMPRESSION_THRESHOLD:
            compressed_path, original_size, compressed_size = self.compress_file(file_path)
            if compressed_path != file_path:
                file_path = compressed_path
                is_compressed = True

        # Generate preview/thumbnail
        thumbnail_path = None
        preview_path = None

        if generate_preview:
            ext = self.get_file_extension(original_filename)

            # Decompress temporarily if needed for preview generation
            temp_path = file_path
            if is_compressed:
                temp_dir = os.path.join(self.base_upload_folder, 'temp')
                os.makedirs(temp_dir, exist_ok=True)
                temp_path = self.decompress_file(file_path, os.path.join(temp_dir, unique_filename))

            # Generate previews based on file type
            if ext in self.ALLOWED_EXTENSIONS['images']:
                # Images: generate thumbnail
                thumbnail_path = self.generate_image_thumbnail(temp_path)
            elif ext == 'pdf':
                # PDFs: generate preview from first page and thumbnail
                preview_path = self.generate_pdf_preview(temp_path)
                if preview_path:
                    # Also generate thumbnail from preview
                    thumbnail_path = self.generate_image_thumbnail(preview_path)
            elif ext in self.ALLOWED_EXTENSIONS['videos']:
                # Videos: generate thumbnail from frame
                thumbnail_path = self.generate_video_thumbnail(temp_path)

            # Clean up temp file
            if is_compressed and temp_path != file_path and os.path.exists(temp_path):
                os.remove(temp_path)

        # Extract metadata
        metadata = self.extract_file_metadata(file_path)

        return {
            'original_filename': original_filename,
            'stored_filename': unique_filename,
            'file_path': file_path,
            'file_size': file_size,
            'compressed_size': compressed_size if is_compressed else file_size,
            'is_compressed': is_compressed,
            'compression_ratio': (1 - compressed_size / file_size) * 100 if is_compressed else 0,
            'thumbnail_path': thumbnail_path,
            'preview_path': preview_path,
            'metadata': metadata
        }

    def delete_file(self, file_path: str, delete_related: bool = True) -> bool:
        """
        Delete file and optionally its related files (thumbnails, previews).

        Args:
            file_path: Path to file to delete
            delete_related: Whether to delete related files (thumbnails, previews)

        Returns:
            True if deletion successful, False otherwise
        """
        try:
            # Delete main file
            if os.path.exists(file_path):
                os.remove(file_path)

            # Delete related files
            if delete_related:
                filename = os.path.basename(file_path)

                # Delete thumbnail
                thumbnail_path = os.path.join(self.base_upload_folder, 'thumbnails', f"thumb_{filename}")
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)

                # Delete preview
                preview_path = os.path.join(self.base_upload_folder, 'previews', f"preview_{filename}.jpg")
                if os.path.exists(preview_path):
                    os.remove(preview_path)

                # Delete compressed version if exists
                if not file_path.endswith('.gz'):
                    compressed_path = f"{file_path}.gz"
                    if os.path.exists(compressed_path):
                        os.remove(compressed_path)

            return True

        except Exception as e:
            current_app.logger.error(f"Failed to delete file {file_path}: {str(e)}")
            return False

    def delete_entity_files(self, entity_type: str, entity_id: int) -> Dict:
        """
        Delete all files for an entity (cascading delete).

        Args:
            entity_type: Type of entity (activity, group, member, meeting)
            entity_id: ID of entity

        Returns:
            Dictionary with deletion statistics
        """
        entity_dir = self.get_storage_path(entity_type, entity_id)

        deleted_count = 0
        failed_count = 0
        total_size_freed = 0

        if os.path.exists(entity_dir):
            for filename in os.listdir(entity_dir):
                file_path = os.path.join(entity_dir, filename)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    if self.delete_file(file_path, delete_related=True):
                        deleted_count += 1
                        total_size_freed += file_size
                    else:
                        failed_count += 1

            # Remove directory if empty
            try:
                if not os.listdir(entity_dir):
                    os.rmdir(entity_dir)
            except Exception:
                pass

        return {
            'deleted_count': deleted_count,
            'failed_count': failed_count,
            'total_size_freed': total_size_freed,
            'size_freed_mb': round(total_size_freed / (1024 * 1024), 2)
        }

    def get_storage_usage(self, entity_type: str = None, entity_id: int = None) -> Dict:
        """
        Get storage usage statistics.

        Args:
            entity_type: Optional entity type to filter by
            entity_id: Optional entity ID to filter by

        Returns:
            Dictionary with storage statistics
        """
        if entity_type and entity_id:
            # Get usage for specific entity
            entity_dir = self.get_storage_path(entity_type, entity_id)
            if not os.path.exists(entity_dir):
                return {
                    'total_files': 0,
                    'total_size': 0,
                    'total_size_mb': 0,
                    'by_category': {}
                }

            total_size = 0
            file_count = 0
            by_category = {}

            for filename in os.listdir(entity_dir):
                file_path = os.path.join(entity_dir, filename)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    file_count += 1

                    category = self.get_file_category(self.get_file_extension(filename))
                    if category not in by_category:
                        by_category[category] = {'count': 0, 'size': 0}
                    by_category[category]['count'] += 1
                    by_category[category]['size'] += file_size

            return {
                'total_files': file_count,
                'total_size': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'by_category': by_category
            }

        else:
            # Get overall usage
            total_size = 0
            file_count = 0
            by_entity_type = {}

            for entity_type_dir in ['activities', 'groups', 'members', 'meetings']:
                entity_path = os.path.join(self.base_upload_folder, entity_type_dir)
                if os.path.exists(entity_path):
                    for entity_id_dir in os.listdir(entity_path):
                        entity_full_path = os.path.join(entity_path, entity_id_dir)
                        if os.path.isdir(entity_full_path):
                            for filename in os.listdir(entity_full_path):
                                file_path = os.path.join(entity_full_path, filename)
                                if os.path.isfile(file_path):
                                    file_size = os.path.getsize(file_path)
                                    total_size += file_size
                                    file_count += 1

                                    if entity_type_dir not in by_entity_type:
                                        by_entity_type[entity_type_dir] = {'count': 0, 'size': 0}
                                    by_entity_type[entity_type_dir]['count'] += 1
                                    by_entity_type[entity_type_dir]['size'] += file_size

            return {
                'total_files': file_count,
                'total_size': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'total_size_gb': round(total_size / (1024 * 1024 * 1024), 2),
                'by_entity_type': by_entity_type
            }

    def cleanup_orphaned_files(self, dry_run: bool = True) -> Dict:
        """
        Find and optionally delete orphaned files (files without database records).

        Args:
            dry_run: If True, only report what would be deleted without actually deleting

        Returns:
            Dictionary with cleanup statistics
        """
        # This would require database access to check which files are orphaned
        # Implementation would be added in the documents.py file where we have db access
        return {
            'message': 'Orphaned file cleanup requires database access',
            'dry_run': dry_run
        }


# Singleton instance
_file_storage_service = None


def get_file_storage_service() -> FileStorageService:
    """Get or create file storage service singleton."""
    global _file_storage_service
    if _file_storage_service is None:
        _file_storage_service = FileStorageService()
    return _file_storage_service

