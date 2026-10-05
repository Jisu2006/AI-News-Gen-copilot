import uuid

from dotenv import load_dotenv

load_dotenv()

import cloudinary
import cloudinary.uploader


# ============================================================
# CLOUDINARY CONFIGURATION
# ============================================================

cloudinary.config(
    secure=True
)


# ============================================================
# CHECK CONFIGURATION
# ============================================================

def cloudinary_configured() -> bool:
    """
    Check whether Cloudinary is configured with valid
    cloud name, API key and API secret.
    """

    config = cloudinary.config()

    return bool(
        config.cloud_name
        and config.api_key
        and config.api_secret
    )


# ============================================================
# UPLOAD MEDIA
# ============================================================

def upload_media(
    file_storage,
    resource_type: str,
    folder: str,
) -> str:
    """
    Upload a Flask FileStorage object to Cloudinary.

    resource_type:
        image
        video

    Returns:
        Cloudinary secure HTTPS URL.
    """

    if not file_storage:
        raise ValueError(
            "No file was provided."
        )

    if not getattr(
        file_storage,
        "filename",
        None
    ):
        raise ValueError(
            "File has no filename."
        )

    if not cloudinary_configured():
        raise RuntimeError(
            "Cloudinary is not configured."
        )

    # Always upload from the beginning of the stream.
    file_storage.stream.seek(0)

    public_id = (
        f"{uuid.uuid4().hex}"
    )

    result = cloudinary.uploader.upload(
        file_storage.stream,

        resource_type=resource_type,

        folder=folder,

        public_id=public_id,

        overwrite=False,

        unique_filename=True,

        secure=True,
    )

    secure_url = result.get(
        "secure_url"
    )

    if not secure_url:
        raise RuntimeError(
            "Cloudinary upload succeeded but secure_url was not returned."
        )

    return secure_url