from gridfs import GridFS
from bson import ObjectId


fs = GridFS(db)

def upload_image_to_gridfs(file_obj, filename=None, content_type=None):
    """
    Uploads a file-like object to GridFS and returns the file ID.
    """
    try:
        file_id = fs.put(
            file_obj.read(),
            filename=filename or getattr(file_obj, 'name', 'file'),
            content_type=content_type or getattr(file_obj, 'content_type', 'application/octet-stream')
        )
        return file_id
    except Exception as e:
        raise RuntimeError(f"GridFS upload failed: {str(e)}")

def get_file_from_gridfs(file_id):
    """
    Retrieves a file from GridFS by ID.
    """
    try:
        return fs.get(ObjectId(file_id))
    except Exception:
        return None
