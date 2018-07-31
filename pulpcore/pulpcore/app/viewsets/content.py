from gettext import gettext as _

from django.db import models, transaction
from rest_framework import status, mixins
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from pulpcore.app.models import Artifact, Content, ContentArtifact
from pulpcore.app.serializers import ArtifactSerializer, ContentSerializer
from pulpcore.app.viewsets import BaseFilterSet, NamedModelViewSet


class ArtifactFilter(BaseFilterSet):
    """
    Artifact filter Plugin content filters should:
     - inherit from this class
     - add any plugin-specific filters if needed
     - define its own `Meta` class should:
       - specify plugin content model
       - extend `fields` with plugin-specific ones
    """
    class Meta:
        model = Artifact
        fields = ['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512']


class ArtifactViewSet(NamedModelViewSet,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin):
    endpoint_name = 'artifacts'
    queryset = Artifact.objects.all()
    serializer_class = ArtifactSerializer
    filterset_class = ArtifactFilter
    parser_classes = (MultiPartParser, FormParser)

    def destroy(self, request, pk):
        """
        Remove Artifact only if it is not associated with any Content.
        """
        try:
            return super().destroy(request, pk)
        except models.ProtectedError:
            msg = _('The Artifact cannot be deleted because it is associated with Content.')
            data = {'detail': msg}
            return Response(data, status=status.HTTP_409_CONFLICT)
