# Django Libraries
from django.db.models import Model, CharField, IntegerField, DateTimeField

class APIRequestStats(Model):
    """
    Main database model for storing API request stats.
    """
    path         = CharField(max_length=128)
    method       = CharField(max_length=6)
    client_ip    = CharField(max_length=15)
    client_user  = CharField(max_length=36)
    client_group = CharField(max_length=36)
    endpoint     = CharField(max_length=128)
    user_agent   = CharField(max_length=256)
    retcode      = IntegerField()
    req_size     = IntegerField()
    rsp_size     = IntegerField()
    rsp_time_ms  = IntegerField()
    created      = DateTimeField(auto_now_add=True)
    
    # Custom table metadata
    class Meta:
        db_table = 'api_stats_request'