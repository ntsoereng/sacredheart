from pathlib import Path
from uuid import uuid4

from django.core.files.storage import FileSystemStorage


class SafeMediaStorage(FileSystemStorage):
    """Give uploaded files non-executable, unpredictable filenames."""

    allowed_extensions = {
        ".gif",
        ".jpeg",
        ".jpg",
        ".png",
        ".pdf",
        ".webp",
    }

    def get_valid_name(self, name):
        extension = Path(name).suffix.lower()
        if extension not in self.allowed_extensions:
            extension = ".bin"
        return f"{uuid4().hex}{extension}"
