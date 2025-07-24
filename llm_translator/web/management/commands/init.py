import web.models as models
import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from web.schemas import TranslationSpecDefinitionSchema, SpecTestCaseDefinitionSchema
from web.constants import EngineOptions, ExpectationResult


class Command(BaseCommand):
    help = "Init database"

    def handle(self, *args, **kwargs):

        user = User.objects.get_or_create(username="admin")[0]
        acc = models.Account.objects.create(name="Default Account", user=user)
        api_key = models.AccountAPIKey.objects.create(account=acc, key="default_key")


        self.__order_create_sample_endpoint(acc)
    
    def __order_create_sample_endpoint(self, acc):
        default_endpoint = models.TranslationEndpoint.objects.create(
            key="default",
            name="Jedi JSON's Order Create to XML's Star Trek Enterprise",
            definition={},
            owner=acc,
        )

        models.TranslationSpec.objects.create(
            is_active=False,
            name="Dynamic Spec",
            endpoint=models.TranslationEndpoint.objects.first(),
            definition=TranslationSpecDefinitionSchema(
                input_rule={
                    "content_type": "json",
                },
                output_rule={
                    "content_type": "xml",
                },
                extra_context="""
[DATE FORMAT]
- All dates must be formatted as DD/MM/YYYY

[FIELDS]
- Output field names must follow snake_case

[OUTPUT FORMAT]
- Must return a raw XML payload without breaklines or indentation
""",
            ).model_dump(),
            version="0.0.0",
        )

        # Compiled Artifact spec
        compiled_artifact_spec = models.TranslationSpec.objects.create(
            name="Compiled Artifact Spec",
            endpoint=models.TranslationEndpoint.objects.first(),
            is_active=True,
            definition=TranslationSpecDefinitionSchema(
                engine= EngineOptions.COMPILED_ARTIFACT,
                input_rule={
                    "content_type": "json",
                },
                output_rule={
                    "content_type": "xml",
                },
                extra_context="""
[DATE FORMAT]
- All dates must be formatted as DD/MM/YYYY

""",
            ).model_dump(),
            version="0.0.1",
        )

        samples_path = "llm_translator/web/samples/starwars/order_create"
        models.SpecTestCase.objects.create(
            name="001 - Order Create",
            spec=compiled_artifact_spec,
            definition=SpecTestCaseDefinitionSchema(
                **{
                    "input": {
                        "body": open(f"{samples_path}/001/input.json").read(),
                        "content_type": "json",
                    },
                    "expectation": {
                        "body": open(f"{samples_path}/001/expected.xml").read(),
                        "content_type": "xml",
                        "result": ExpectationResult.SUCESS,
                    },
                }
            ).model_dump(),
        )

        # Import random
        import random

        statuses = [
            models.TranslationEventStatus.SUCCESS,
            models.TranslationEventStatus.FAILURE,
        ]

        # Random sampling of 300 events varying between success and failure and timestamps
        for i in range(1000):
            event = models.TranslationEvent.objects.create(
                status=statuses[random.randint(0, 1)],
                context={},
                endpoint=default_endpoint,
            )

            event.created_at = event.created_at - datetime.timedelta(
                days=random.randint(0, 30)
            )
            event.save()

        # Create sample events
        models.TranslationEvent.objects.create(
            status=models.TranslationEventStatus.SUCCESS,
            context={},
            endpoint=default_endpoint,
        )
