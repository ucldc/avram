from django.core.exceptions import ValidationError
from django import forms
from django.db import models

class HeroField(models.ImageField):
    description = "Hero Image must be 200px by 800px"
    
    def __init__(self, *args, **kwargs):
        super(HeroField, self).__init__(*args, **kwargs)
    
    def formfield(self, **kwargs):
        defaults = {'form_class': HeroFormField}
        defaults.update(kwargs)
        return super(HeroField, self).formfield(**defaults)

    def pre_save(self, model_instance, add):
        return getattr(model_instance, self.attname)

class HeroFormField(forms.ImageField):
    def to_python(self, data):
        if data in self.empty_values: 
            return None
        
        try: 
            file_name = data.name
            file_size = data.size
        except AttributeError:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        
        if self.max_length is not None and len(file_name) > self.max_length:
            params = {'max': self.max_length, 'length': len(file_name)}
            raise ValidationError(self.error_messages['max_length'], code='max_length', params=params)
        if not file_name:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        if not self.allow_empty_file and not file_size:
            raise ValidationError(self.error_messages['empty'], code='empty')
        
        return data.name
