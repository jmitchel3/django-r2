import pathlib
import uuid
from typing import Optional

from django.utils.text import slugify


def create_s3_filename(
    fname,
    object_id: Optional[uuid.UUID | str] = None,
    id_max_length: int = 10,
):
    if fname is None:
        return None
    if fname == "":
        return None
    fpath = pathlib.Path(fname)
    stem = fpath.stem
    if object_id:
        object_id = str(object_id)
        stem = f"{stem}_{object_id[:id_max_length]}"
    suffix = fpath.suffix
    stem_clean = slugify(stem).replace("-", "_")
    return f"{stem_clean}{suffix}"
