from django.contrib import admin
#from django.utils.html import format_html
from .models import Project, LabelCategory, Dataset, Image, Video, Annotation, AnnotationSession
#from .widgets import ColorPickerWidget


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'created_at', 'updated_at']
    list_filter = ['created_at', 'owner']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LabelCategory)
class LabelCategoryAdmin(admin.ModelAdmin):
#    list_display = ['name', 'project', 'annotation_type', 'color_preview', 'created_at']
    list_display = ['name', 'project', 'annotation_type', 'color', 'created_at']
    list_filter = ['annotation_type', 'project', 'created_at']
    search_fields = ['name', 'project__name']
    
#    def color_preview(self, obj):
#        return format_html(
#            '<div class="admin-color-preview">'
#            '<div class="admin-color-swatch" style="background-color: {};"></div>'
#            '<span>{}</span>'
#            '</div>',
#            obj.color,
#            obj.color
#        )
#    color_preview.short_description = 'Color'
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
#        if db_field.name == 'color':
#            kwargs['widget'] = ColorPickerWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
#    class Media:
#        css = {
#            'all': ('admin/css/colorpicker.css',)
#        }
#        js = ('admin/js/colorpicker.js',)


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'dataset_type', 'created_at']
    list_filter = ['dataset_type', 'created_at', 'project']
    search_fields = ['name', 'description', 'project__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['filename', 'dataset', 'width', 'height', 'size', 'is_annotated', 'uploaded_at']
    list_filter = ['is_annotated', 'uploaded_at', 'dataset']
    search_fields = ['filename', 'dataset__name']
    readonly_fields = ['filename', 'width', 'height', 'size', 'uploaded_at']


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['filename', 'dataset', 'duration', 'fps', 'width', 'height', 'uploaded_at']
    list_filter = ['uploaded_at', 'dataset']
    search_fields = ['filename', 'dataset__name']
    readonly_fields = ['filename', 'duration', 'fps', 'width', 'height', 'size', 'uploaded_at']


@admin.register(Annotation)
class AnnotationAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'label_category', 'annotation_type', 'annotator', 'created_at']
    list_filter = ['annotation_type', 'label_category', 'annotator', 'created_at']
    search_fields = ['label_category__name', 'annotator__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AnnotationSession)
class AnnotationSessionAdmin(admin.ModelAdmin):
    list_display = ['annotator', 'dataset', 'start_time', 'end_time', 'annotations_count']
    list_filter = ['start_time', 'annotator', 'dataset']
    search_fields = ['annotator__username', 'dataset__name']
