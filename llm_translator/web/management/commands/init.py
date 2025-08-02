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
            name="JSON to XML",
            definition={},
            owner=acc,
        )

        # XML to JSON endpoint
        xml_to_json_endpoint = models.TranslationEndpoint.objects.create(
            key="xml-to-json",
            name="XML to JSON",
            definition={},
            owner=acc,
        )

        # YAML to JSON endpoint
        yaml_to_json_endpoint = models.TranslationEndpoint.objects.create(
            key="yaml-to-json",
            name="YAML to JSON",
            definition={},
            owner=acc,
        )

        # JSON to YAML endpoint
        json_to_yaml_endpoint = models.TranslationEndpoint.objects.create(
            key="json-to-yaml",
            name="JSON to YAML",
            definition={},
            owner=acc,
        )

        # CSV to JSON endpoint
        csv_to_json_endpoint = models.TranslationEndpoint.objects.create(
            key="csv-to-json",
            name="CSV to JSON",
            definition={},
            owner=acc,
        )

        # Default endpoint dynamic spec
        default_spec = models.TranslationSpec.objects.create(
            is_active=True,
            name="Default Dynamic Spec",
            endpoint=default_endpoint,
            definition=TranslationSpecDefinitionSchema(
                engine=EngineOptions.DYNAMIC,
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

[CONVERSION RULES]
- Convert JSON structure to XML format
- Preserve data types and structure
- Handle nested objects and arrays appropriately
- Use snake_case for XML element names
""",
            ).model_dump(),
            version="0.0.1",
        )

        # XML to JSON spec
        xml_to_json_spec = models.TranslationSpec.objects.create(
            name="XML to JSON Spec",
            endpoint=xml_to_json_endpoint,
            is_active=True,
            definition=TranslationSpecDefinitionSchema(
                engine=EngineOptions.DYNAMIC,
                input_rule={
                    "content_type": "xml",
                },
                output_rule={
                    "content_type": "json",
                },
                extra_context="""
[CONVERSION RULES]
- Convert XML elements to JSON objects
- Convert XML attributes to JSON properties with '@' prefix
- Convert XML text content to 'text' property when mixed with elements
- Handle nested structures appropriately
- Preserve data types (strings, numbers, booleans)
- Use camelCase for field names in output JSON
""",
            ).model_dump(),
            version="0.0.1",
        )

        # YAML to JSON spec
        yaml_to_json_spec = models.TranslationSpec.objects.create(
            name="YAML to JSON Spec",
            endpoint=yaml_to_json_endpoint,
            is_active=True,
            definition=TranslationSpecDefinitionSchema(
                engine=EngineOptions.DYNAMIC,
                input_rule={
                    "content_type": "yaml",
                },
                output_rule={
                    "content_type": "json",
                },
                extra_context="""
[CONVERSION RULES]
- Convert YAML structure to equivalent JSON structure
- Preserve data types (strings, numbers, booleans, arrays, objects)
- Handle YAML anchors and aliases by expanding them
- Convert YAML comments to JSON comments where possible
- Use camelCase for field names in output JSON
- Preserve nested object and array structures
""",
            ).model_dump(),
            version="0.0.1",
        )

        # JSON to YAML spec
        json_to_yaml_spec = models.TranslationSpec.objects.create(
            name="JSON to YAML Spec",
            endpoint=json_to_yaml_endpoint,
            is_active=True,
            definition=TranslationSpecDefinitionSchema(
                engine=EngineOptions.DYNAMIC,
                input_rule={
                    "content_type": "json",
                },
                output_rule={
                    "content_type": "yaml",
                },
                extra_context="""
[CONVERSION RULES]
- Convert JSON structure to equivalent YAML structure
- Preserve data types (strings, numbers, booleans, arrays, objects)
- Use camelCase for field names in output YAML
- Preserve nested object and array structures
- Format YAML with proper indentation (2 spaces)
- Handle special characters and escaping appropriately
""",
            ).model_dump(),
            version="0.0.1",
        )

        # CSV to JSON spec
        csv_to_json_spec = models.TranslationSpec.objects.create(
            name="CSV to JSON Spec",
            endpoint=csv_to_json_endpoint,
            is_active=True,
            definition=TranslationSpecDefinitionSchema(
                engine=EngineOptions.DYNAMIC,
                input_rule={
                    "content_type": "csv",
                },
                output_rule={
                    "content_type": "json",
                },
                extra_context="""
[CONVERSION RULES]
- Convert CSV data to JSON array of objects
- Use first row as column headers (field names)
- Convert each subsequent row to a JSON object
- Handle empty cells appropriately
- Preserve data types where possible (strings, numbers, booleans)
- Use camelCase for field names in output JSON
- Handle special characters and escaping in CSV values
""",
            ).model_dump(),
            version="0.0.1",
        )

        # Compiled Artifact spec
        compiled_artifact_spec = models.TranslationSpec.objects.create(
            name="Compiled Artifact Spec",
            endpoint=models.TranslationEndpoint.objects.first(),
            is_active=True,
            definition=TranslationSpecDefinitionSchema(
                engine=EngineOptions.COMPILED_ARTIFACT,
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
        # import random

        # statuses = [
        #     models.TranslationEventStatus.SUCCESS,
        #     models.TranslationEventStatus.FAILURE,
        # ]

        # # Random sampling of 300 events varying between success and failure and timestamps
        # for i in range(1000):
        #     event = models.TranslationEvent.objects.create(
        #         status=statuses[random.randint(0, 1)],
        #         context={},
        #         endpoint=default_endpoint,
        #     )

        #     event.created_at = event.created_at - datetime.timedelta(
        #         days=random.randint(0, 30)
        #     )
        #     event.save()

        # # Create sample events
        # models.TranslationEvent.objects.create(
        #     status=models.TranslationEventStatus.SUCCESS,
        #     context={},
        #     endpoint=default_endpoint,
        # )
