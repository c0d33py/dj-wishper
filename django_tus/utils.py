import logging

from django_tus.models import TusFileModel


logger = logging.getLogger(__name__)


def get_tus_media(data, obj):
    resources_arry = data.split(",")

    for resource_id in resources_arry:
        try:
            # Get the file object
            file = TusFileModel.objects.get(guid=str(resource_id))
            # Update file path & object_id
            file.content_object = obj
            file.save()
            return logger.info("File uploaded successfully")
        except TusFileModel.DoesNotExist:
            return logger.error("File does not exist")
