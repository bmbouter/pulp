from django.contrib.contenttypes.models import ContentType
from pulpcore.app.models import Artifact, Content, ContentArtifact, ProgressBar, RepositoryContent


def orphan_cleanup():
    """
    Delete all orphan Content and Artifact records.
    This task removes Artifact files from the filesystem as well.
    """
    # Content cleanup
    for content_type in ContentType.objects.all():
        if issubclass(content_type.model_class(), Content):
            non_orphans = RepositoryContent.objects.filter(
                version_removed=None).values_list('object_id', flat=True)
            content_qs = content_type.model_class().objects.exclude(pk__in=non_orphans)
            msg = 'Clean up orphan content of type: {type}'.format(type=content_type.name)
            with ProgressBar(message=msg, total=content_qs.count(), done=0, state='running') as pb:
                content_qs.delete()
                pb.done = pb.total

    # Artifact cleanup
    artifacts = Artifact.objects.exclude(pk__in=ContentArtifact.objects.values_list('artifact_id',
                                                                                    flat=True))
    progress_bar = ProgressBar(message='Clean up orphan Artifacts', total=artifacts.count(),
                               done=0, state='running')
    progress_bar.save()
    for artifact in artifacts:
        # we need to manually call delete() because it cleans up the file on the filesystem
        artifact.delete()
        progress_bar.increment()

    progress_bar.state = 'completed'
    progress_bar.save()
