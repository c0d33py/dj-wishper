import logging
from celery import shared_task

from .transcribe import Transcribe

logger = logging.getLogger(__name__)


# @shared_task
@shared_task(time_limit=300, soft_time_limit=240)
def get_transcript(file_id):
    transcriber = Transcribe()  # Initialize
    logger.info('File Transcript process is running!')
    transcriber.transcribe_file(file_id)
