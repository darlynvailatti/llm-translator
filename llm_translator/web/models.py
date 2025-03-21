import uuid
from django.db import models
from django.db.models.base import Model
from django.db.models import JSONField
from .constants import TranslationEventStatus, TranslationArtifcatImplType, TranslationTestCaseStatus
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

class TranslationArtifact(BaseModel):
    spec = models.ForeignKey("TranslationSpec", on_delete=models.CASCADE)
    implementation = models.BinaryField()
    implementation_type = models.CharField(max_length=128, default=TranslationArtifcatImplType.PYTHON,
        choices=[
            (TranslationArtifcatImplType.PYTHON, TranslationArtifcatImplType.PYTHON), 
        ]
    )

    @property
    def implementation_str(self):
        return self.implementation.tobytes().decode("utf-8")
    
    def __str__(self):
        return f"{self.spec.name} - {self.implementation_str}"

class TranslationSpec(BaseModel):
    is_active = models.BooleanField(default=False)
    name = models.CharField(max_length=256)
    endpoint = models.ForeignKey(TranslationEndpoint, on_delete=models.CASCADE)
    definition = JSONField()
    version = models.CharField(max_length=128)

    def __str__(self):
        return self.name
    
class SpecTestCase(BaseModel):
    name = models.CharField(max_length=256)
    definition = JSONField()
    spec = models.ForeignKey(TranslationSpec, on_delete=models.CASCADE)
    executed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=128, choices=[
        (TranslationTestCaseStatus.SUCCESS, TranslationTestCaseStatus.SUCCESS), 
        (TranslationTestCaseStatus.FAILURE, TranslationEventStatus.FAILURE),
        (TranslationTestCaseStatus.NOT_EXECUTED, TranslationTestCaseStatus.NOT_EXECUTED)],
        default=TranslationTestCaseStatus.NOT_EXECUTED
    )



class TranslationEvent(BaseModel):
    status = models.CharField(max_length=128, choices=[
        (TranslationEventStatus.SUCCESS, TranslationEventStatus.SUCCESS), 
        (TranslationEventStatus.SUCCESS, TranslationEventStatus.FAILURE)]
    )
    context = JSONField()
    endpoint = models.ForeignKey(TranslationEndpoint, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.endpoint.name} - {self.status} - {self.created_at}"





