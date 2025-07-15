import cloudinary
import cloudinary.uploader
import os

# Load env variables (if not loaded already)
from dotenv import load_dotenv
load_dotenv()

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
)

def upload_image_to_cloudinary(image_file):
    try:
        result = cloudinary.uploader.upload(image_file)
        return result.get("secure_url")
    except Exception as e:
        raise Exception(f"Cloudinary upload failed: {str(e)}")
