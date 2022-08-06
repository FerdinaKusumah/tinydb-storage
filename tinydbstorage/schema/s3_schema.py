from pydantic import BaseModel


class S3ConfigSchema(BaseModel):
    aws_bucket_name: str
    aws_file_path: str
    aws_region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
