DEFAULT_REDIS_KEY = "tiny_db"

DEFAULT_S3_REGION = "ap-southeast-1"
JSON_CONTENT_TYPE = "application/json"
S3_MISSING_OBJECT_CODES = frozenset({"NoSuchKey", "NotFound", "404"})
# NoSuchKey on a write means the object read earlier was deleted before If-Match.
S3_CONFLICT_CODES = frozenset(
    {"PreconditionFailed", "ConditionalRequestConflict", "NoSuchKey", "412", "409"}
)
