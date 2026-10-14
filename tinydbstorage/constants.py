DEFAULT_REDIS_KEY = "tiny_db"

DEFAULT_S3_REGION = "ap-southeast-1"
JSON_CONTENT_TYPE = "application/json"
S3_MISSING_OBJECT_CODES = frozenset({"NoSuchKey", "NotFound", "404"})
S3_CONFLICT_CODES = frozenset(
    {"PreconditionFailed", "ConditionalRequestConflict", "412", "409"}
)
