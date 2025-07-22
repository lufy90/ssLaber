from django import forms
from django.forms import widgets


class ColorPickerWidget(widgets.TextInput):
    """
    A custom widget that renders a color input field with a color picker.
    """
    input_type = 'color'
    template_name = 'admin/widgets/colorpicker.html'
    
    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-control color-picker'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    class Media:
        css = {
            'all': ('admin/css/colorpicker.css',)
        }
        js = ('admin/js/colorpicker.js',)
    
    def format_value(self, value):
        if value is None:
            return ''
        if isinstance(value, str) and value.startswith('#') and len(value) == 7:
            return value
        return f'#{value}' if value and not value.startswith('#') else value or '#FF0000'