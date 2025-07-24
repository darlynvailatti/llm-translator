# Django Signals

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SpecTestCaseExecution

@receiver(post_save, sender=SpecTestCaseExecution)
def create_translation_endpoint(sender, instance, created, **kwargs):

    test_case = instance.test_case
    test_case.executed_at = instance.executed_at
    test_case.status = instance.status
    test_case.save()