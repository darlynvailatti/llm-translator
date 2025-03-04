import web.models as models

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from web.schemas import TranslationSpecDefinitionSchema


class Command(BaseCommand):
    help = "Init database"

    def handle(self, *args, **kwargs):

        user = User.objects.get_or_create(username="admin")[0]
        acc = models.Account.objects.create(name="Default Account", user=user)
        api_key = models.AccountAPIKey.objects.create(account=acc, key="default_key")

        models.TranslationEndpoint.objects.create(
            key="default",
            name="Default Endpoint",
            definition={},
            owner=acc,
        )

        models.TranslationSpec.objects.create(
            name="Default Spec",
            endpoint=models.TranslationEndpoint.objects.first(),
            is_active=True,
            definition=TranslationSpecDefinitionSchema(
                input_rule={
                    "content_type": "application/json",
                },
                output_rule={
                    "content_type": "application/json",
                },
                extra_context="""
                [DATE FORMAT]
                - All dates must be formatted as DD/MM/YYYY

                [FIELDS]
                - Output field names must follow snake_case

                [OUTPUT FORMAT]
                - Must return a raw JSON payload without breaklines or indentation

                """,
            ).model_dump(),
            version="0.0.0",
        )
