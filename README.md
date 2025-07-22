# Image Labeling Tool

A comprehensive web-based image annotation platform built with Django, designed for creating high-quality datasets for machine learning model training.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/django-5.2+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### 🎯 **Core Functionality**
- **Project-based organization** - Organize annotations by projects and datasets
- **Multi-format support** - Handle images (JPG, PNG, BMP, TIFF) and videos (MP4, AVI, MOV, MKV)
- **Real-time annotation** - Interactive canvas-based annotation interface
- **User management** - Multi-user support with authentication
- **Export capabilities** - Export to COCO and YOLO formats

### 🖼️ **Annotation Tools**
- **Bounding Box** - Drag-to-create rectangular annotations
- **Polygon** - Multi-point polygon annotations (planned)
- **Keypoints** - Point-based annotations (planned)
- **Classification** - Image-level labels
- **Preview overlays** - See annotations on image thumbnails

### 📊 **Data Management**
- **Batch upload** - Upload multiple images at once
- **Annotation tracking** - Track annotation progress and statistics
- **Label categories** - Color-coded labels with different annotation types
- **Session management** - Track annotation sessions and productivity

### 🚀 **Export Options**
- **COCO Format** - Industry-standard JSON format
- **YOLO Format** - Ready-to-train YOLO datasets with labels and images
- **Comprehensive documentation** - Auto-generated README files with export

## 🛠️ Technology Stack

- **Backend**: Django 5.2+ (Python)
- **Frontend**: Bootstrap 5, JavaScript (ES6+), SVG Canvas
- **Database**: SQLite (default) / PostgreSQL (production)
- **Authentication**: Django Auth System
- **File Storage**: Django File Storage (local/cloud)

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd annotation
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install django pillow
```

### 4. Database Setup
```bash
# Run database migrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser
```

### 5. Start Development Server
```bash
python manage.py runserver
```

### 6. Access the Application
- **Main Application**: http://localhost:8000
- **Admin Interface**: http://localhost:8000/admin
- **Login**: Use the superuser account you created

## 📖 Usage Guide

### Creating Your First Project

1. **Login** to the application
2. **Create a new project** from the dashboard
3. **Add label categories** through the admin interface
4. **Create a dataset** within your project
5. **Upload images** to the dataset
6. **Start annotating** using the annotation interface

### Annotation Workflow

1. **Select a label** from the toolbar
2. **Choose annotation tool** (Bounding Box recommended)
3. **Click and drag** on the image to create annotations
4. **Save annotations** using the Save button
5. **Export dataset** when annotation is complete

### Export Process

1. Navigate to dataset detail page
2. Click the **"Export"** dropdown
3. Choose format:
   - **COCO Format** - JSON file with COCO standard
   - **YOLO Labels Only** - Annotation files only
   - **YOLO with Images** - Complete training dataset
4. Download and use with your ML framework

## 📁 Project Structure

```
annotation/
├── 📁 annotation/           # Django project settings
│   ├── settings.py         # Configuration
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI application
├── 📁 labeling/            # Main application
│   ├── 📁 models/          # Data models
│   ├── 📁 views/           # View logic
│   ├── 📁 templates/       # HTML templates
│   ├── 📁 static/          # CSS, JS, images
│   └── 📁 migrations/      # Database migrations
├── 📁 media/               # Uploaded files
├── 📁 static/              # Static assets
├── manage.py               # Django management
└── README.md               # This file
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional - defaults to SQLite)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Media files
MEDIA_ROOT=/path/to/media/files
STATIC_ROOT=/path/to/static/files
```

### Production Settings

For production deployment:

1. Set `DEBUG = False`
2. Configure `ALLOWED_HOSTS`
3. Use PostgreSQL database
4. Set up proper static file serving
5. Configure secure secret key

## 🔧 Development

### Running Tests
```bash
python manage.py test
```

### Database Migration
```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Creating Superuser
```bash
python manage.py createsuperuser
```

### Static Files Collection
```bash
python manage.py collectstatic
```

## 📦 Data Models

### Core Models
- **Project** - Top-level organization unit
- **Dataset** - Collection of images/videos
- **Image/Video** - Media files with metadata
- **LabelCategory** - Annotation label definitions
- **Annotation** - Individual annotations with coordinates
- **AnnotationSession** - User session tracking

### Supported Annotation Types
- `bbox` - Bounding boxes (implemented)
- `polygon` - Polygon shapes (planned)
- `keypoint` - Point annotations (planned)
- `classification` - Image labels
- `segmentation` - Pixel-wise masks (planned)

## 🌐 API Endpoints

### Authentication
- `GET /login/` - Login page
- `POST /logout/` - Logout endpoint

### Projects & Datasets
- `GET /` - Project list
- `GET /projects/<id>/` - Project detail
- `GET /datasets/<id>/` - Dataset detail
- `POST /datasets/<id>/upload/` - Image upload

### Annotations
- `GET /images/<id>/annotate/` - Annotation interface
- `GET /api/annotations/` - List annotations
- `POST /api/annotations/` - Create annotation
- `PUT /api/annotations/<id>/` - Update annotation
- `DELETE /api/annotations/<id>/` - Delete annotation

### Export
- `GET /export/<dataset_id>/coco/` - COCO export
- `GET /export/<dataset_id>/yolo/` - YOLO export
- `GET /export/<dataset_id>/yolo/?include_images=true` - YOLO with images

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues

**Q: Images not loading**
A: Check MEDIA_ROOT and MEDIA_URL settings, ensure proper file permissions

**Q: Annotations not saving**
A: Verify CSRF token is present, check browser console for JavaScript errors

**Q: Export fails**
A: Ensure proper write permissions for temporary directories

### Getting Help

- Check the [Issues](../../issues) page for known problems
- Create a new issue for bug reports or feature requests
- Review Django documentation for framework-specific questions

## 🔄 Version History

- **v1.0.0** - Initial release with core annotation features
- **v1.1.0** - Added YOLO export and improved UI
- **v1.2.0** - Enhanced annotation tools and preview overlays

## 🎯 Roadmap

- [ ] Video annotation support
- [ ] Polygon and keypoint annotation tools
- [ ] Advanced export options (Pascal VOC, TensorFlow)
- [ ] Collaborative annotation features
- [ ] API improvements and documentation
- [ ] Mobile-responsive annotation interface

---

**Made with ❤️ for the Computer Vision Community**

*Happy Annotating! 🏷️*