import cloudinary
import cloudinary.uploader

def upload_to_cloudinary(file, resource_type):
    if not file or not resource_type:
        return {'secure_url': None}
    
    try:
        upload_result = cloudinary.uploader.upload(file, resource_type=resource_type)
        return upload_result
    except Exception as e:
        print("Error uploading file to Cloudinary:", e)
        return {'secure_url': None}
    
    