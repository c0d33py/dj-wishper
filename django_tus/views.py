import base64
import logging

from rest_framework import views, status, permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import Response

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from django_tus.conf import settings
from django_tus.models import TusFileModel
from django_tus.response import TusResponse
from django_tus.signals import tus_upload_finished_signal
from django_tus.tusfile import TusFile, TusChunk, FilenameGenerator
from pathvalidate._filename import is_valid_filename


logger = logging.getLogger(__name__)

TUS_SETTINGS = {}


class TusUpload(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    on_finish = None

    # @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        if not self.request.META.get("HTTP_TUS_RESUMABLE"):
            return TusResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED, content="Method Not Allowed")

        override_method = self.request.META.get('HTTP_X_HTTP_METHOD_OVERRIDE')
        if override_method:
            self.request.method = override_method
        return super(TusUpload, self).dispatch(*args, **kwargs)

    def finished(self):
        if self.on_finish is not None:
            self.on_finish()

    def get_metadata(self, request):
        metadata = {}
        if request.META.get("HTTP_UPLOAD_METADATA"):
            for kv in request.META.get("HTTP_UPLOAD_METADATA").split(","):
                splited_metadata = kv.split(" ")
                if len(splited_metadata) == 2:
                    key, value = splited_metadata
                    value = base64.b64decode(value)
                    if isinstance(value, bytes):
                        value = value.decode()
                    metadata[key] = value
                else:
                    metadata[splited_metadata[0]] = ""
        return metadata

    def options(self, request, *args, **kwargs):
        return TusResponse(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, *args, **kwargs):

        metadata = self.get_metadata(request)

        metadata["filename"] = self.validate_filename(metadata)

        message_id = request.META.get("HTTP_MESSAGE_ID")
        if message_id:
            metadata["message_id"] = base64.b64decode(message_id)

        if settings.TUS_EXISTING_FILE == 'error' and settings.TUS_FILE_NAME_FORMAT == 'keep' and TusFile.check_existing_file(metadata.get("filename")):
            return TusResponse(status=status.HTTP_409_CONFLICT, reason="File with same name already exists")

        file_size = int(request.META.get("HTTP_UPLOAD_LENGTH", "0"))  # TODO: check min max upload size

        tus_file = TusFile.create_initial_file(metadata, file_size)

        return TusResponse(
            status=status.HTTP_201_CREATED,
            extra_headers={'Location': '{}{}'.format(request.build_absolute_uri(), tus_file.resource_id)})

    def head(self, request, resource_id):
        tus_file = TusFile.get_tusfile_or_404(str(resource_id))
        return TusResponse(status=status.HTTP_200_OK,
                           extra_headers={
                               'Upload-Offset': tus_file.offset,
                               'Upload-Length': tus_file.file_size})

    def patch(self, request, resource_id, *args, **kwargs):

        tus_file = TusFile.get_tusfile_or_404(str(resource_id))
        chunk = TusChunk(request)

        if not tus_file.is_valid():
            return TusResponse(status=status.HTTP_410_GONE)

        if chunk.offset != tus_file.offset:
            return TusResponse(status=status.HTTP_409_CONFLICT)

        if chunk.offset > tus_file.file_size:
            return TusResponse(status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        tus_file.write_chunk(chunk=chunk)

        if tus_file.is_complete():
            # file transfer complete, rename from resource id to actual filename
            tus_file.rename()
            tus_file.clean()

            self.send_signal(tus_file)
            self.finished()

        return TusResponse(status=status.HTTP_204_NO_CONTENT, extra_headers={'Upload-Offset': tus_file.offset})

    def send_signal(self, tus_file):
        tus_upload_finished_signal.send(
            sender=self.__class__,
            resource_id=tus_file.resource_id,
            metadata=tus_file.metadata,
            filename=tus_file.filename,
            upload_file_path=tus_file.get_path(),
            file_size=tus_file.file_size,
            upload_url=settings.TUS_UPLOAD_URL,
            destination_folder=settings.TUS_DESTINATION_DIR)

    def validate_filename(self, metadata):
        filename = metadata.get("filename", "")
        if not is_valid_filename(filename):
            filename = FilenameGenerator.random_string(16)
        return filename

    def delete(self, request, resource_id, *args, **kwargs):
        try:
            tus_file = TusFile.get_tusfile_or_404(str(resource_id))
            tus_file.get_existing_object(resource_id).delete()
            tus_file.clean()
        except Exception as e:
            TusFileModel.objects.filter(guid=resource_id).delete()
        return TusResponse(status=status.HTTP_204_NO_CONTENT)


class TusUploadDelete(views.APIView):
    ''' Delete file and remove from database '''
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, resource_id=None, format=None):
        objects = get_object_or_404(TusFileModel, guid=resource_id)
        objects.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
