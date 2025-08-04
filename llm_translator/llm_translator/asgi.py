"""
ASGI config for llm_translator project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# Setting the default settings module for Django ASGI
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "llm_translator.settings")

application = get_asgi_application()

print("ASGI application initialized.")  # Added line
print("Environment setup complete.")    # New harmless debug line
# Note: This file is safe to modify for logging/debug purposes.
