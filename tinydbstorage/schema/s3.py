from pydantic import BaseModel


class S3Schema(BaseModel):
    """
    Represents a schema for interacting with Amazon S3.

    :param file_path: The file path in the S3 bucket.
    :type file_path: str
    :param bucket_name: The name of the S3 bucket.
    :type bucket_name: str
    :param region_name: The AWS region of the S3 bucket.
    :type region_name: str
    :param access_key_id: The AWS access key ID for authentication.
    :type access_key_id: str
    :param secret_access_key: The AWS secret access key for authentication.
    :type secret_access_key: str
    """

    file_path: str
    bucket_name: str
    region_name: str
    access_key_id: str
    secret_access_key: str

    @classmethod
    def from_param(
        cls,
        file_path: str,
        bucket_name: str,
        region_name: str,
        access_key: str,
        secret_key: str,
    ) -> "S3Schema":
        """
        Create an instance of S3Schema from individual parameters.

        :param file_path: The file path in the S3 bucket.
        :type file_path: str
        :param bucket_name: The name of the S3 bucket.
        :type bucket_name: str
        :param region_name: The AWS region of the S3 bucket.
        :type region_name: str
        :param access_key: The AWS access key ID for authentication.
        :type access_key: str
        :param secret_key: The AWS secret access key for authentication.
        :type secret_key: str

        :return: An instance of S3Schema.
        :rtype: S3Schema
        """
        return S3Schema(
            file_path=file_path,
            bucket_name=bucket_name,
            region_name=region_name,
            access_key_id=access_key,
            secret_access_key=secret_key,
        )
