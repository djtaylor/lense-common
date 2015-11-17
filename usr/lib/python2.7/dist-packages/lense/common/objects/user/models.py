from uuid import uuid4

# Django Libraries
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.db.models import Model, CharField,DateTimeField, ForeignKey, EmailField, BooleanField

# Lense Libraries
from lense.common.objects.user.manager import APIUserManager
from lense.common.objects.group.models import APIGroups, APIGroupMembers

class APIUserKeys(Model):
    """
    Main database model for storing user API keys.
    """
    
    # User API key table columns
    user    = ForeignKey('user.APIUser', to_field='uuid', db_column='user')
    api_key = CharField(max_length=64, unique=True)
    
    # Custom model metadata
    class Meta:
        db_table = 'api_user_keys'
        
class APIUserTokens(models.Model):
    """
    Main database model for storing user API tokens.
    """
    
    # User API token table columns
    user    = models.ForeignKey('user.APIUser', to_field='uuid', db_column='user')
    token   = models.CharField(max_length=255, unique=True)
    expires = models.DateTimeField()
    
    # Custom model metadata
    class Meta:
        db_table = 'api_user_tokens'

class APIUser(AbstractBaseUser):
    """
    Main database model for user accounts.
    """
    uuid        = CharField(max_length=36, unique=True, default=str(uuid4()))
    first_name  = CharField(_('first name'), max_length=30, blank=True)
    last_name   = CharField(_('last name'), max_length=30, blank=True)
    email       = EmailField(_('email address'), blank=True)
    date_joined = DateTimeField(_('date joined'), default=timezone.now)
    from_ldap   = BooleanField(_('LDAP User'), editable=False, default=False)
    
    # Username
    username    = CharField(_('username'),
        max_length = 30, 
        unique     = True,
        help_text  = _('Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators = [
            RegexValidator(r'^[\w.@+-]+$',
            _('Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.'), 
            'invalid'),
        ],
        error_messages = {
            'unique': _("A user with that username already exists."),
        })
    
    # Is the account active
    is_active   = BooleanField(_('active'), 
        default   = True,
        help_text = _('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')
    )

    # User objects manager
    objects = APIUserManager()

    # Username field and required fields
    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    # Model metadata
    class Meta:
        db_table = 'lense_users'
        verbose_name = _('user')
        verbose_name_plural = _('users')