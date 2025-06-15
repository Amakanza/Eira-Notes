import io
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from app.core.config import settings


class StorageService:
    """Service for handling file storage operations using AWS S3."""
    
    def __init__(self):
        """Initialize the storage service with AWS S3 client."""
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket_name = settings.S3_BUCKET_NAME
    
    async def upload_file(
        self, file: UploadFile, folder: str = "uploads"
    ) -> Tuple[str, str]:
        """Upload a file to S3 and return the file path and filename."""
        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
        new_filename = f"{timestamp}_{unique_id}.{file_extension}"
        
        # Create the S3 key (path)
        s3_key = f"{folder}/{new_filename}"
        
        # Read the file content
        content = await file.read()
        
        # Upload to S3
        self.s3_client.upload_fileobj(
            io.BytesIO(content),
            self.bucket_name,
            s3_key,
            ExtraArgs={
                "ContentType": file.content_type,
            },
        )
        
        return s3_key, new_filename
    
    def generate_presigned_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """Generate a presigned URL for accessing a file."""
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": file_path,
                },
                ExpiresIn=expires_in,
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file from S3."""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path,
            )
            return True
        except ClientError as e:
            print(f"Error deleting file: {e}")
            return False


# Create a singleton instance
storage_service = StorageService()