import json

# Django Libraries
from django.db import models
from django.utils import six
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator

class JSONField(models.TextField):
    """
    Custom Django model field for storing JSON data strings.
    """
    
    # Field description
    description = _('JSON')
    
    def __init__(self, empty=False, *args, **kwargs):
        
        # Only accept boolean values for the <empty> attribute
        if not isinstance(empty, bool):
            raise ValidationError('JSONField model keyword <empty> must be either true or false')
        
        # Empty values flag
        self.empty = empty
        
        # If empty JSON values are allowed
        if self.empty:
            kwargs['blank'] = True
            kwargs['null']  = True
        
        # Construct the parent field
        super(JSONField, self).__init__(*args, **kwargs)
    
    def get_db_prep_value(self, value, connection, prepared=False):
        """
        Except both an object and a string. Make sure both are in valid JSON
        format and return a string.
        """
        
        # If the value is empty
        if not value:
            if not self.empty == True:
                raise ValidationError('JSONField value cannot be empty, must set the model\'s <empty> attribute to true to enable')
            return None
        
        # If the data type is invalid
        if not isinstance(value, (list, dict, six.string_types)):
            raise ValidationError('JSONField value invalid data {}, only accepts <dict>, <list>, or <str>'.format(repr(type(value))))
        
        # If saving a list or dictionary
        if isinstance(value, (list, dict)):
            
            # Make sure the object is valid JSON
            try:
                return json.dumps(value)
                
            # Invalid format
            except Exception as e:
                raise ValidationError('JSONField value of {} cannot be converted to JSON string: {}'.format(repr(type(value)), str(e)))
            
        # If saving a string
        if isinstance(value, six.string_types):
        
            # Make sure the string can be converted to a valid JSON object
            try:
                json_obj = json.loads(value)
                
                # Return the string value
                return value
            
            # Invalid format
            except Exception as e:
                raise ValidationError('JSONField value of {} cannot be converted to JSON object: {}'.format(repr(type(value)), str(e)))

class NullTextField(models.TextField):
    """
    Custom Django model field for null capable text fields.
    """
    
    # Field description
    description = _('NullText')
    
    def __init__(self, *args, **kwargs):

        # Allow null/blank values
        kwargs['blank'] = True
        kwargs['null']  = True
        
        # Construct the parent field class
        super(NullTextField, self).__init__(*args, **kwargs)

class NullForeignKey(models.ForeignKey):
    """
    Custom Django model field for null capable foreign key relationships.
    """
    
    # Field description
    description = _('NullForeignKey')
    
    def __init__(self, *args, **kwargs):

        # Allow null/blank values
        kwargs['blank'] = True
        kwargs['null']  = True
        
        # Set to null on delete of parent key
        kwargs['on_delete'] = models.SET_NULL

        # Construct the parent field class
        super(NullForeignKey, self).__init__(*args, **kwargs)