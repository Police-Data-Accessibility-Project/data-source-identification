from src.external.internet_archives.models.archive_metadata import IAArchiveMetadata
from src.external.internet_archives.models.capture import IACapture


def convert_capture_to_archive_metadata(capture: IACapture) -> IAArchiveMetadata:
    archive_url = f"https://web.archive.org/web/{capture.timestamp}/{capture.original}"
    return IAArchiveMetadata(
        archive_url=archive_url,
        length=capture.length,
        digest=capture.digest
    )