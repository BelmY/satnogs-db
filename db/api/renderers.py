"""SatNOGS DB django rest framework API custom renderers"""
from rest_framework.renderers import JSONRenderer

from db.base.structured_data import get_structured_data


class JSONLDRenderer(JSONRenderer):
    """ Renderer which serializes to JSONLD. """

    media_type = 'application/ld+json'
    format = 'json-ld'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """ Render `data` into JSONLD, returning a bytestring. """
        structured_data = get_structured_data(renderer_context['view'].basename, data)
        jsonld = structured_data.get_jsonld()
        return super(JSONLDRenderer, self).render(jsonld, accepted_media_type, renderer_context)
