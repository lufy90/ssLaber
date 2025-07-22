from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import uuid
import os


def upload_to_images(instance, filename):
    return os.path.join('images', str(instance.dataset.id), filename)


def upload_to_videos(instance, filename):
    return os.path.join('videos', str(instance.dataset.id), filename)


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class LabelCategory(models.Model):
    ANNOTATION_TYPES = [
        ('bbox', 'Bounding Box'),
        ('polygon', 'Polygon'),
        ('keypoint', 'Keypoint'),
        ('classification', 'Classification'),
        ('segmentation', 'Segmentation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='labels')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#FF0000')
    annotation_type = models.CharField(max_length=20, choices=ANNOTATION_TYPES, default='bbox')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.name} - {self.name}"

    class Meta:
        unique_together = ['project', 'name']
        ordering = ['name']


class Dataset(models.Model):
    DATASET_TYPES = [
        ('image', 'Image Dataset'),
        ('video', 'Video Dataset'),
        ('sequential', 'Sequential Images'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='datasets')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    dataset_type = models.CharField(max_length=20, choices=DATASET_TYPES, default='image')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project.name} - {self.name}"

    class Meta:
        ordering = ['-created_at']


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='images')
    file = models.ImageField(
        upload_to=upload_to_images,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'bmp', 'tiff'])]
    )
    filename = models.CharField(max_length=255)
    width = models.IntegerField()
    height = models.IntegerField()
    size = models.BigIntegerField()
    sequence_number = models.IntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_annotated = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.file:
            self.filename = os.path.basename(self.file.name)
            self.size = self.file.size
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.dataset.name} - {self.filename}"

    class Meta:
        ordering = ['sequence_number', 'filename']
        unique_together = ['dataset', 'filename']


class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='videos')
    file = models.FileField(
        upload_to=upload_to_videos,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov', 'mkv'])]
    )
    filename = models.CharField(max_length=255)
    duration = models.FloatField(null=True, blank=True)
    fps = models.FloatField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    size = models.BigIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.file:
            self.filename = os.path.basename(self.file.name)
            self.size = self.file.size
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.dataset.name} - {self.filename}"

    class Meta:
        ordering = ['filename']


class Annotation(models.Model):
    ANNOTATION_TYPES = [
        ('bbox', 'Bounding Box'),
        ('polygon', 'Polygon'),
        ('keypoint', 'Keypoint'),
        ('classification', 'Classification'),
        ('segmentation', 'Segmentation'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='annotations', null=True, blank=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='annotations', null=True, blank=True)
    frame_number = models.IntegerField(null=True, blank=True)
    timestamp = models.FloatField(null=True, blank=True)
    
    label_category = models.ForeignKey(LabelCategory, on_delete=models.CASCADE)
    annotation_type = models.CharField(max_length=20, choices=ANNOTATION_TYPES)
    
    # Bounding box coordinates (x, y, width, height)
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    width = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    
    # Polygon/segmentation points stored as JSON
    points = models.JSONField(null=True, blank=True)
    
    # Additional metadata
    confidence = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    annotator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        target = self.image.filename if self.image else f"{self.video.filename}:{self.frame_number}"
        return f"{target} - {self.label_category.name}"

    class Meta:
        ordering = ['-created_at']


class AnnotationSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='sessions')
    annotator = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    annotations_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.annotator.username} - {self.dataset.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-start_time']
