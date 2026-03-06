"""
Comprehensive configuration settings for New00 project
"""

import os
from typing import Dict, Any, List, Tuple

class ProjectConfig:
    """Main configuration class for New00 project"""
    
    # Application Configuration
    APP_NAME = "New00 - Complete Document & Image Processing Suite"
    VERSION = "1.0.0"
    DESCRIPTION = "Complete suite for PDF and image processing with modern GUI"
    
    # Server Configuration
    SERVER = {
        'host': '0.0.0.0',
        'port': 5000,
        'debug': False,
        'secret_key': 'dev-secret-key-change-in-production'
    }
    
    # File Upload Configuration
    UPLOAD = {
        'max_size_mb': 200,
        'max_size_bytes': 200 * 1024 * 1024,
        'folder': 'uploads',
        'allowed_extensions': {
            # PDF files
            'pdf': ['.pdf'],
            # Image files  
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'],
            # Document files
            'documents': ['.docx', '.xlsx', '.pptx']
        }
    }
    
    # PDF Processing Configuration
    PDF_CONFIG = {
        'default_dpi': 150,
        'max_dpi': 300,
        'compression': {
            'levels': ['low', 'medium', 'high', 'maximum'],
            'settings': {
                'low': {'dpi': 100, 'quality': 50},
                'medium': {'dpi': 150, 'quality': 75},
                'high': {'dpi': 200, 'quality': 85},
                'maximum': {'dpi': 300, 'quality': 95}
            }
        },
        'watermark': {
            'default_text': 'CONFIDENTIAL',
            'default_font_size': 50,
            'default_opacity': 0.5,
            'default_rotation': 45,
            'positions': ['center', 'top-left', 'top-right', 'bottom-left', 'bottom-right']
        },
        'page_numbers': {
            'default_format': 'Page {n}',
            'default_position': 'bottom-center',
            'default_font_size': 12
        }
    }
    
    # Image Processing Configuration
    IMAGE_CONFIG = {
        'max_size_mb': 50,
        'max_size_bytes': 50 * 1024 * 1024,
        'default_quality': 90,
        'thumbnail_size': (200, 200),
        'preview_size': (800, 600),
        'adjustments': {
            'brightness': {'min': 0, 'max': 200, 'default': 100},
            'contrast': {'min': 0, 'max': 200, 'default': 100},
            'saturation': {'min': 0, 'max': 200, 'default': 100}
        },
        'effects': {
            'blur': {'min': 0, 'max': 10, 'default': 2},
            'sharpen': {'min': 0, 'max': 10, 'default': 1}
        },
        'background_removal': {
            'default_tolerance': 30,
            'tolerance_range': (0, 100),
            'strength_levels': {
                'conservative': {'threshold': 220, 'variance': 20},
                'moderate': {'threshold': 200, 'variance': 30},
                'aggressive': {'threshold': 180, 'variance': 40}
            }
        }
    }
    
    # API Configuration
    API = {
        'version': 'v1',
        'prefix': '/api/v1',
        'rate_limit': '100 per hour',
        'timeout': 30,
        'cors_origins': [
            'http://localhost:5000',
            'http://localhost:5001',
            'http://127.0.0.1:5000',
            'http://127.0.0.1:5001'
        ]
    }
    
    # Security Configuration
    SECURITY = {
        'csrf_enabled': True,
        'secure_cookies': False,  # Enable in production
        'max_request_size': 200 * 1024 * 1024,
        'allowed_hosts': ['localhost', '127.0.0.1']
    }
    
    # Logging Configuration
    LOGGING = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'new00.log',
        'max_size_mb': 10,
        'backup_count': 5
    }
    
    # Cache Configuration
    CACHE = {
        'type': 'simple',  # simple, redis, memcached
        'timeout': 300,  # 5 minutes
        'key_prefix': 'new00_',
        'max_entries': 1000
    }
    
    # Database Configuration (if needed)
    DATABASE = {
        'url': 'sqlite:///new00.db',
        'echo': False,
        'pool_size': 10,
        'max_overflow': 20
    }
    
    # External Tools Configuration
    EXTERNAL_TOOLS = {
        'tesseract': {
            'path': '',
            'executable': 'tesseract',
            'languages': ['eng', 'spa', 'fra', 'deu'],
            'default_language': 'eng'
        },
        'ghostscript': {
            'path': '',
            'executable': 'gswin64c',  # Windows
            'alternative': 'gs',  # Linux/Mac
            'device': 'pdfwrite'
        },
        'libreoffice': {
            'path': '',
            'executable': 'soffice',
            'timeout': 30
        }
    }
    
    # UI Configuration
    UI = {
        'theme': 'light',  # light, dark, auto
        'language': 'en',
        'items_per_page': 20,
        'auto_save': True,
        'auto_save_interval': 300,  # 5 minutes
        'history_limit': 50,
        'preview_quality': 85
    }
    
    # Performance Configuration
    PERFORMANCE = {
        'max_concurrent_uploads': 5,
        'processing_timeout': 300,  # 5 minutes
        'chunk_size': 8192,
        'memory_limit_mb': 512,
        'temp_cleanup_interval': 3600  # 1 hour
    }

class DevelopmentConfig(ProjectConfig):
    """Development configuration"""
    SERVER = {
        **ProjectConfig.SERVER,
        'debug': True,
        'port': 5000
    }
    LOGGING = {
        **ProjectConfig.LOGGING,
        'level': 'DEBUG'
    }
    SECURITY = {
        **ProjectConfig.SECURITY,
        'secure_cookies': False
    }

class ProductionConfig(ProjectConfig):
    """Production configuration"""
    SERVER = {
        **ProjectConfig.SERVER,
        'debug': False,
        'port': 80
    }
    LOGGING = {
        **ProjectConfig.LOGGING,
        'level': 'WARNING'
    }
    SECURITY = {
        **ProjectConfig.SECURITY,
        'secure_cookies': True
    }

class TestingConfig(ProjectConfig):
    """Testing configuration"""
    SERVER = {
        **ProjectConfig.SERVER,
        'debug': True,
        'port': 5001
    }
    LOGGING = {
        **ProjectConfig.LOGGING,
        'level': 'DEBUG'
    }
    SECURITY = {
        **ProjectConfig.SECURITY,
        'csrf_enabled': False
    }
    DATABASE = {
        **ProjectConfig.DATABASE,
        'url': 'sqlite:///:memory:'
    }

# Configuration mapping
CONFIG_MAP = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: str = None) -> ProjectConfig:
    """Get configuration by name"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return CONFIG_MAP.get(config_name, CONFIG_MAP['default'])

# Utility functions
def is_allowed_extension(filename: str, file_type: str = 'all') -> bool:
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    
    ext = '.' + filename.rsplit('.', 1)[1].lower()
    
    if file_type == 'all':
        all_exts = []
        for exts in ProjectConfig.UPLOAD['allowed_extensions'].values():
            all_exts.extend(exts)
        return ext in all_exts
    elif file_type in ProjectConfig.UPLOAD['allowed_extensions']:
        return ext in ProjectConfig.UPLOAD['allowed_extensions'][file_type]
    
    return False

def get_file_type(filename: str) -> str:
    """Get file type category"""
    if '.' not in filename:
        return 'unknown'
    
    ext = '.' + filename.rsplit('.', 1)[1].lower()
    
    for file_type, extensions in ProjectConfig.UPLOAD['allowed_extensions'].items():
        if ext in extensions:
            return file_type
    
    return 'unknown'

def get_mime_type(filename: str) -> str:
    """Get MIME type for file"""
    ext = '.' + filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    mime_types = {
        '.pdf': 'application/pdf',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp',
        '.tiff': 'image/tiff',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    }
    
    return mime_types.get(ext, 'application/octet-stream')

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def validate_quality(quality: int) -> int:
    """Validate and normalize quality value"""
    return max(1, min(100, quality))

def validate_dpi(dpi: int) -> int:
    """Validate and normalize DPI value"""
    return max(50, min(600, dpi))

def get_environment() -> str:
    """Get current environment"""
    return os.environ.get('FLASK_ENV', 'development')

def is_production() -> bool:
    """Check if running in production"""
    return get_environment() == 'production'

def is_development() -> bool:
    """Check if running in development"""
    return get_environment() == 'development'

def is_testing() -> bool:
    """Check if running in testing"""
    return get_environment() == 'testing'

# Feature flags
FEATURES = {
    'pdf_tools': True,
    'image_tools': True,
    'gui_editor': True,
    'batch_processing': True,
    'ocr': True,
    'background_removal': True,
    'real_time_preview': True,
    'undo_redo': True,
    'api_access': True,
    'file_sharing': True
}

# Version information
VERSION_INFO = {
    'major': 1,
    'minor': 0,
    'patch': 0,
    'build': 'dev',
    'full': '1.0.0-dev'
}

# Dependencies information
DEPENDENCIES = {
    'required': [
        'Flask>=3.0.0',
        'PyMuPDF>=1.24.0',
        'Pillow>=10.0.0',
        'Werkzeug>=3.0.0'
    ],
    'optional': [
        'pytesseract>=0.3.10',  # OCR
        'pypdf>=5.1.0',         # PDF processing
        'reportlab>=4.2.5',       # PDF generation
        'numpy>=1.24.0',          # Image processing
        'redis>=4.0.0',           # Caching
        'psycopg2>=2.9.0'         # PostgreSQL
    ],
    'dev': [
        'pytest>=7.0.0',
        'black>=22.0.0',
        'flake8>=5.0.0',
        'mypy>=1.0.0'
    ]
}
