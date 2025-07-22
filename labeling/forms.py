from django import forms
from django.forms import modelformset_factory
from .models import Project, Dataset, Image, Annotation, LabelCategory


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DatasetForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ['name', 'description', 'dataset_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'dataset_type': forms.Select(attrs={'class': 'form-control'}),
        }


class ImageUploadForm(forms.Form):
    images = MultipleFileField(
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text='Select one or more image files to upload.'
    )


class LabelCategoryForm(forms.ModelForm):
    class Meta:
        model = LabelCategory
        fields = ['name', 'color', 'annotation_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'annotation_type': forms.Select(attrs={'class': 'form-control'}),
        }


class AnnotationForm(forms.ModelForm):
    class Meta:
        model = Annotation
        fields = ['label_category', 'annotation_type', 'x', 'y', 'width', 'height', 'points', 'confidence', 'notes']
        widgets = {
            'label_category': forms.Select(attrs={'class': 'form-control'}),
            'annotation_type': forms.Select(attrs={'class': 'form-control'}),
            'x': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'y': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'confidence': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


LabelCategoryFormSet = modelformset_factory(
    LabelCategory,
    form=LabelCategoryForm,
    extra=1,
    can_delete=True
)