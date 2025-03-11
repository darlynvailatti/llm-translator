import uuid
from django.db import models
from django.db.models.base import Model
from django.db.models import JSONField

class BaseModel(Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Account(BaseModel):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class AccountAPIKey(BaseModel):
    key = models.CharField(max_length=128, default=uuid.uuid4, unique=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.account.name} - {self.key}"
    

class TranslationEndpoint(BaseModel):
    key = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=256)
    is_active = models.BooleanField(default=True)
    definition = JSONField()
    owner = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    @property
    def total_success(self):
        return TranslationEvent.objects.filter(endpoint=self, status=TranslationEventStatus.SUCCESS).count()
    
    @property
    def total_failure(self):
        return TranslationEvent.objects.filter(endpoint=self, status=TranslationEventStatus.FAILURE).count()
    
class TranslationSpec(BaseModel):
    is_active = models.BooleanField(default=False)
    name = models.CharField(max_length=256)
    endpoint = models.ForeignKey(TranslationEndpoint, on_delete=models.CASCADE)
    definition = JSONField()
    version = models.CharField(max_length=128)
    
    def __str__(self):
        return self.name

class TranslationEventStatus:
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"

class TranslationEvent(BaseModel):
    status = models.CharField(max_length=128, choices=[
        (TranslationEventStatus.SUCCESS, TranslationEventStatus.SUCCESS), 
        (TranslationEventStatus.SUCCESS, TranslationEventStatus.FAILURE)]
    )
    context = JSONField()
    endpoint = models.ForeignKey(TranslationEndpoint, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.endpoint.name} - {self.status} - {self.created_at}"





