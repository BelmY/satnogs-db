"""
NOTE this is a patch to add missing functionality from DRF's openapi implementation
and should be revisited periodically as new functionality is implemented upstream.
refer to https://github.com/encode/django-rest-framework/pull/7516
"""

from rest_framework.schemas.openapi import SchemaGenerator as OpenAPISchemaGenerator


class SchemaGenerator(OpenAPISchemaGenerator):
    """
    Returns an extended schema that includes some missing fields from the
    upstream OpenAPI implementation
    """
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)

        schema['info']['version'] = '1.0'

        # temporarily add servers until the following is fixed
        # https://github.com/encode/django-rest-framework/issues/7631
        schema['servers'] = [
            {
                'url': 'http://localhost:8000',
                'description': 'local dev'
            }, {
                'url': 'https://db.satnogs.org',
                'description': 'production'
            }
        ]

        # temporarily add securitySchemes until implemented upstream
        if 'securitySchemes' not in schema['components']:
            schema['components']['securitySchemes'] = {
                'ApiKeyAuth': {
                    'type': 'apiKey',
                    'in': 'header',
                    'name': 'Authorization'
                }
            }

        # temporarily add default security object at top-level
        if 'security' not in schema:
            schema['security'] = [{'ApiKeyAuth': []}]

        return schema
