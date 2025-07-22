from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.files.storage import default_storage
from django.forms import modelformset_factory
from PIL import Image as PILImage
import json
import os

from .models import Project, Dataset, Image, Video, Annotation, LabelCategory, AnnotationSession
from .forms import ProjectForm, DatasetForm, ImageUploadForm, AnnotationForm


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'labeling/project_list.html'
    context_object_name = 'projects'
    
    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'labeling/project_detail.html'
    context_object_name = 'project'
    
    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'labeling/project_form.html'
    success_url = reverse_lazy('labeling:project_list')
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'labeling/project_form.html'
    
    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('labeling:project_detail', kwargs={'pk': self.object.pk})


class DatasetCreateView(LoginRequiredMixin, CreateView):
    model = Dataset
    form_class = DatasetForm
    template_name = 'labeling/dataset_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['project_id'], owner=self.request.user)
        return context
    
    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'], owner=self.request.user)
        form.instance.project = project
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('labeling:project_detail', kwargs={'pk': self.kwargs['project_id']})


class DatasetDetailView(LoginRequiredMixin, DetailView):
    model = Dataset
    template_name = 'labeling/dataset_detail.html'
    context_object_name = 'dataset'
    
    def get_queryset(self):
        return Dataset.objects.filter(project__owner=self.request.user)


class DatasetUpdateView(LoginRequiredMixin, UpdateView):
    model = Dataset
    form_class = DatasetForm
    template_name = 'labeling/dataset_form.html'
    
    def get_queryset(self):
        return Dataset.objects.filter(project__owner=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('labeling:dataset_detail', kwargs={'pk': self.object.pk})


class ImageUploadView(LoginRequiredMixin, View):
    template_name = 'labeling/image_upload.html'
    
    def get(self, request, pk):
        dataset = get_object_or_404(Dataset, pk=pk, project__owner=request.user)
        form = ImageUploadForm()
        return render(request, self.template_name, {'dataset': dataset, 'form': form})
    
    def post(self, request, pk):
        dataset = get_object_or_404(Dataset, pk=pk, project__owner=request.user)
        files = request.FILES.getlist('images')
        
        if not files:
            messages.error(request, 'No files selected.')
            return redirect('labeling:image_upload', pk=pk)
        
        uploaded_count = 0
        for file in files:
            try:
                with PILImage.open(file) as img:
                    width, height = img.size
                
                image = Image.objects.create(
                    dataset=dataset,
                    file=file,
                    width=width,
                    height=height
                )
                uploaded_count += 1
            except Exception as e:
                messages.error(request, f'Error uploading {file.name}: {str(e)}')
        
        if uploaded_count:
            messages.success(request, f'Successfully uploaded {uploaded_count} images.')
        
        return redirect('labeling:dataset_detail', pk=pk)


class ImageDetailView(LoginRequiredMixin, DetailView):
    model = Image
    template_name = 'labeling/image_detail.html'
    context_object_name = 'image'
    
    def get_queryset(self):
        return Image.objects.filter(dataset__project__owner=self.request.user)


class AnnotationView(LoginRequiredMixin, View):
    template_name = 'labeling/annotate.html'
    
    def get(self, request, pk):
        image = get_object_or_404(Image, pk=pk, dataset__project__owner=request.user)
        labels = LabelCategory.objects.filter(project=image.dataset.project)
        annotations = Annotation.objects.filter(image=image)
        
        context = {
            'image': image,
            'labels': labels,
            'annotations': annotations,
            'annotations_json': json.dumps([{
                'id': str(ann.id),
                'label_id': str(ann.label_category.id),
                'label_name': ann.label_category.name,
                'type': ann.annotation_type,
                'x': ann.x,
                'y': ann.y,
                'width': ann.width,
                'height': ann.height,
                'points': ann.points,
                'color': ann.label_category.color
            } for ann in annotations])
        }
        return render(request, self.template_name, context)


class AnnotationAPIView(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        if pk:
            annotation = get_object_or_404(Annotation, pk=pk)
            data = {
                'id': str(annotation.id),
                'label_id': str(annotation.label_category.id),
                'label_name': annotation.label_category.name,
                'type': annotation.annotation_type,
                'x': annotation.x,
                'y': annotation.y,
                'width': annotation.width,
                'height': annotation.height,
                'points': annotation.points,
                'confidence': annotation.confidence,
                'notes': annotation.notes
            }
            return JsonResponse(data)
        else:
            image_id = request.GET.get('image_id')
            if image_id:
                annotations = Annotation.objects.filter(image_id=image_id)
                data = [{
                    'id': str(ann.id),
                    'label_id': str(ann.label_category.id),
                    'label_name': ann.label_category.name,
                    'type': ann.annotation_type,
                    'x': ann.x,
                    'y': ann.y,
                    'width': ann.width,
                    'height': ann.height,
                    'points': ann.points,
                    'color': ann.label_category.color
                } for ann in annotations]
                return JsonResponse({'annotations': data})
            return JsonResponse({'error': 'image_id required'}, status=400)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            image = get_object_or_404(Image, pk=data['image_id'])
            label_category = get_object_or_404(LabelCategory, pk=data['label_id'])
            
            annotation = Annotation.objects.create(
                image=image,
                label_category=label_category,
                annotation_type=data['type'],
                x=data.get('x'),
                y=data.get('y'),
                width=data.get('width'),
                height=data.get('height'),
                points=data.get('points'),
                confidence=data.get('confidence'),
                notes=data.get('notes', ''),
                annotator=request.user
            )
            
            image.is_annotated = True
            image.save()
            
            return JsonResponse({
                'id': str(annotation.id),
                'success': True
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def put(self, request, pk):
        try:
            annotation = get_object_or_404(Annotation, pk=pk)
            data = json.loads(request.body)
            
            annotation.x = data.get('x', annotation.x)
            annotation.y = data.get('y', annotation.y)
            annotation.width = data.get('width', annotation.width)
            annotation.height = data.get('height', annotation.height)
            annotation.points = data.get('points', annotation.points)
            annotation.confidence = data.get('confidence', annotation.confidence)
            annotation.notes = data.get('notes', annotation.notes)
            annotation.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def delete(self, request, pk):
        try:
            annotation = get_object_or_404(Annotation, pk=pk)
            annotation.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class ExportDatasetView(LoginRequiredMixin, View):
    def get(self, request, dataset_id, format):
        dataset = get_object_or_404(Dataset, pk=dataset_id, project__owner=request.user)
        include_images = request.GET.get('include_images', 'false').lower() == 'true'
        
        if format == 'coco':
            return self.export_coco(dataset)
        elif format == 'yolo':
            return self.export_yolo(dataset, include_images)
        else:
            return JsonResponse({'error': 'Unsupported format'}, status=400)
    
    def export_coco(self, dataset):
        images = dataset.images.all()
        categories = LabelCategory.objects.filter(project=dataset.project)
        
        coco_data = {
            'info': {
                'description': dataset.description,
                'version': '1.0',
                'year': 2024
            },
            'images': [],
            'annotations': [],
            'categories': []
        }
        
        for idx, category in enumerate(categories, 1):
            coco_data['categories'].append({
                'id': idx,
                'name': category.name,
                'supercategory': 'object'
            })
        
        category_map = {str(cat.id): idx for idx, cat in enumerate(categories, 1)}
        
        for img_idx, image in enumerate(images, 1):
            coco_data['images'].append({
                'id': img_idx,
                'width': image.width,
                'height': image.height,
                'file_name': image.filename
            })
            
            for ann_idx, annotation in enumerate(image.annotations.all()):
                coco_data['annotations'].append({
                    'id': ann_idx + img_idx * 1000,
                    'image_id': img_idx,
                    'category_id': category_map.get(str(annotation.label_category.id)),
                    'bbox': [annotation.x, annotation.y, annotation.width, annotation.height],
                    'area': annotation.width * annotation.height,
                    'iscrowd': 0
                })
        
        response = HttpResponse(
            json.dumps(coco_data, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="{dataset.name}_coco.json"'
        return response
    
    def export_yolo(self, dataset, include_images=False):
        import zipfile
        import tempfile
        import os
        import shutil
        from io import BytesIO
        
        # Create a temporary directory for YOLO files
        with tempfile.TemporaryDirectory() as temp_dir:
            images_dir = os.path.join(temp_dir, 'images')
            labels_dir = os.path.join(temp_dir, 'labels')
            os.makedirs(images_dir, exist_ok=True)
            os.makedirs(labels_dir, exist_ok=True)
            
            # Get all images and categories
            images = dataset.images.all()
            categories = LabelCategory.objects.filter(project=dataset.project)
            
            # Create class mapping (YOLO uses integer class IDs)
            class_mapping = {str(cat.id): idx for idx, cat in enumerate(categories)}
            
            # Create classes.txt file
            classes_file = os.path.join(temp_dir, 'classes.txt')
            with open(classes_file, 'w') as f:
                for category in categories:
                    f.write(f"{category.name}\n")
            
            # Create data.yaml file for YOLO training
            data_yaml = os.path.join(temp_dir, 'data.yaml')
            with open(data_yaml, 'w') as f:
                f.write(f"# Dataset configuration for {dataset.name}\n")
                f.write(f"path: ./  # dataset root dir\n")
                f.write(f"train: images/  # train images (relative to 'path')\n")
                f.write(f"val: images/  # val images (relative to 'path')\n")
                f.write(f"test:  # test images (optional)\n\n")
                f.write(f"# Classes\n")
                f.write(f"nc: {len(categories)}  # number of classes\n")
                f.write(f"names: [")
                for i, category in enumerate(categories):
                    f.write(f"'{category.name}'")
                    if i < len(categories) - 1:
                        f.write(', ')
                f.write("]\n")
            
            # Process each image
            for image in images:
                # Copy image file if requested
                if include_images and image.file:
                    try:
                        image_source_path = image.file.path
                        image_dest_path = os.path.join(images_dir, image.filename)
                        shutil.copy2(image_source_path, image_dest_path)
                    except Exception as e:
                        print(f"Warning: Could not copy image {image.filename}: {e}")
                
                # Create YOLO format annotation file
                label_filename = os.path.splitext(image.filename)[0] + '.txt'
                label_path = os.path.join(labels_dir, label_filename)
                
                # Get annotations for this image
                annotations = image.annotations.filter(annotation_type='bbox')
                
                if annotations.exists():
                    with open(label_path, 'w') as f:
                        for annotation in annotations:
                            # Convert to YOLO format
                            class_id = class_mapping.get(str(annotation.label_category.id), 0)
                            
                            # YOLO format: class_id center_x center_y width height (all normalized 0-1)
                            img_width = image.width
                            img_height = image.height
                            
                            # Convert from top-left corner format to center format
                            center_x = (annotation.x + annotation.width / 2) / img_width
                            center_y = (annotation.y + annotation.height / 2) / img_height
                            norm_width = annotation.width / img_width
                            norm_height = annotation.height / img_height
                            
                            # Ensure values are within [0, 1] range
                            center_x = max(0, min(1, center_x))
                            center_y = max(0, min(1, center_y))
                            norm_width = max(0, min(1, norm_width))
                            norm_height = max(0, min(1, norm_height))
                            
                            f.write(f"{class_id} {center_x:.6f} {center_y:.6f} {norm_width:.6f} {norm_height:.6f}\n")
                else:
                    # Create empty annotation file for images without annotations
                    with open(label_path, 'w') as f:
                        pass  # Empty file
            
            # Create README file
            readme_path = os.path.join(temp_dir, 'README.txt')
            with open(readme_path, 'w') as f:
                f.write(f"YOLO Dataset Export - {dataset.name}\n")
                f.write("=" * 50 + "\n\n")
                f.write("Generated by Image Labeling Tool\n")
                f.write(f"Export Date: {dataset.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Dataset Type: {dataset.get_dataset_type_display()}\n\n")
                
                f.write("OVERVIEW\n")
                f.write("-" * 20 + "\n")
                f.write("This export contains annotation files in YOLO format, ready for training\n")
                f.write("YOLO (You Only Look Once) object detection models.\n\n")
                
                f.write("FILE STRUCTURE\n")
                f.write("-" * 20 + "\n")
                f.write("📁 Root Directory\n")
                f.write("├── 📁 labels/          # YOLO annotation files (.txt)\n")
                if include_images:
                    f.write("├── 📁 images/          # Training images\n")
                f.write("├── 📄 classes.txt      # Class names (one per line)\n")
                f.write("├── 📄 data.yaml        # YOLO dataset configuration\n")
                f.write("└── 📄 README.txt       # This documentation\n\n")
                
                f.write("YOLO ANNOTATION FORMAT\n")
                f.write("-" * 20 + "\n")
                f.write("Each annotation file (.txt) contains one line per object:\n")
                f.write("Format: class_id center_x center_y width height\n\n")
                f.write("Where:\n")
                f.write("• class_id    = Integer class identifier (0-based)\n")
                f.write("• center_x    = X-coordinate of bounding box center (0.0-1.0)\n")
                f.write("• center_y    = Y-coordinate of bounding box center (0.0-1.0)\n")
                f.write("• width       = Bounding box width (0.0-1.0)\n")
                f.write("• height      = Bounding box height (0.0-1.0)\n\n")
                f.write("All coordinates are normalized relative to image dimensions.\n\n")
                
                f.write("DATASET STATISTICS\n")
                f.write("-" * 20 + "\n")
                total_annotations = sum(img.annotations.filter(annotation_type='bbox').count() for img in images)
                f.write(f"📊 Total Images:        {images.count()}\n")
                f.write(f"✅ Annotated Images:    {images.filter(is_annotated=True).count()}\n")
                f.write(f"🏷️  Total Annotations:   {total_annotations}\n")
                f.write(f"📦 Number of Classes:   {len(categories)}\n\n")
                
                f.write("CLASS MAPPING\n")
                f.write("-" * 20 + "\n")
                f.write("ID | Class Name\n")
                f.write("---|------------\n")
                for category in categories:
                    class_id = class_mapping[str(category.id)]
                    f.write(f"{class_id:2d} | {category.name}\n")
                
                f.write(f"\nUSAGE WITH YOLO\n")
                f.write("-" * 20 + "\n")
                f.write("1. Use the data.yaml file to configure your YOLO training\n")
                f.write("2. Place this dataset in your YOLO project directory\n")
                f.write("3. Update the paths in data.yaml if needed\n")
                f.write("4. Train your model: yolo train data=data.yaml\n\n")
                
                if not include_images:
                    f.write("NOTE: This export contains labels only. Add your images to the\n")
                    f.write("'images/' directory to complete the dataset structure.\n\n")
                
                f.write("For more information about YOLO format and training, visit:\n")
                f.write("https://github.com/ultralytics/ultralytics\n")
            
            # Create ZIP file
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add all files to ZIP
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, temp_dir)
                        zip_file.write(file_path, arc_path)
            
            zip_buffer.seek(0)
            
            response = HttpResponse(
                zip_buffer.getvalue(),
                content_type='application/zip'
            )
            response['Content-Disposition'] = f'attachment; filename="{dataset.name}_yolo.zip"'
            return response
