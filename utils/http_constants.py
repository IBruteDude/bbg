
GET = "GET"
POST = "POST"
PUT = "PUT"
PATCH = "PATCH"
DELETE = "DELETE"

CONTINUE = 100  # Continue
SWITCHING_PROTOCOLS = 101  # Switching Protocols
PROCESSING = 102  # Processing
EARLY_HINTS = 103  # Early Hints
CHECKPOINT = 103  # Checkpoint
OK = 200  # OK
CREATED = 201  # Created
ACCEPTED = 202  # Accepted
NON_AUTHORITATIVE_INFORMATION = 203  # Non-Authoritative Information
NO_CONTENT = 204  # No Content
RESET_CONTENT = 205  # Reset Content
PARTIAL_CONTENT = 206  # Partial Content
MULTI_STATUS = 207  # Multi-Status
ALREADY_REPORTED = 208  # Already Reported
IM_USED = 226  # IM Used
MULTIPLE_CHOICES = 300  # Multiple Choices
MOVED_PERMANENTLY = 301  # Moved Permanently
FOUND = 302  # Found
MOVED_TEMPORARILY = 302  # Moved Temporarily
SEE_OTHER = 303  # See Other
NOT_MODIFIED = 304  # Not Modified
USE_PROXY = 305  # Use Proxy
TEMPORARY_REDIRECT = 307  # Temporary Redirect
PERMANENT_REDIRECT = 308  # Permanent Redirect
BAD_REQUEST = 400  # Bad Request
UNAUTHORIZED = 401  # Unauthorized
PAYMENT_REQUIRED = 402  # Payment Required
FORBIDDEN = 403  # Forbidden
NOT_FOUND = 404  # Not Found
METHOD_NOT_ALLOWED = 405  # Method Not Allowed
NOT_ACCEPTABLE = 406  # Not Acceptable
PROXY_AUTHENTICATION_REQUIRED = 407  # Proxy Authentication Required
REQUEST_TIMEOUT = 408  # Request Timeout
CONFLICT = 409  # Conflict
GONE = 410  # Gone
LENGTH_REQUIRED = 411  # Length Required
PRECONDITION_FAILED = 412  # Precondition Failed
PAYLOAD_TOO_LARGE = 413  # Payload Too Large
REQUEST_ENTITY_TOO_LARGE = 413  # Request Entity Too Large
URI_TOO_LONG = 414  # URI Too Long
REQUEST_URI_TOO_LONG = 414  # Request-URI Too Long
UNSUPPORTED_MEDIA_TYPE = 415  # Unsupported Media Type
REQUESTED_RANGE_NOT_SATISFIABLE = 416  # Requested range not satisfiable
EXPECTATION_FAILED = 417  # Expectation Failed
I_AM_A_TEAPOT = 418  # I'm a teapot
INSUFFICIENT_SPACE_ON_RESOURCE = 419  # Insufficient Space On Resource
METHOD_FAILURE = 420  # Method Failure
DESTINATION_LOCKED = 421  # Destination Locked
UNPROCESSABLE_ENTITY = 422  # Unprocessable Entity
LOCKED = 423  # Locked
FAILED_DEPENDENCY = 424  # Failed Dependency
TOO_EARLY = 425  # Too Early
UPGRADE_REQUIRED = 426  # Upgrade Required
PRECONDITION_REQUIRED = 428  # Precondition Required
TOO_MANY_REQUESTS = 429  # Too Many Requests
REQUEST_HEADER_FIELDS_TOO_LARGE = 431  # Request Header Fields Too Large
UNAVAILABLE_FOR_LEGAL_REASONS = 451  # Unavailable For Legal Reasons
INTERNAL_SERVER_ERROR = 500  # Internal Server Error
NOT_IMPLEMENTED = 501  # Not Implemented
BAD_GATEWAY = 502  # Bad Gateway
SERVICE_UNAVAILABLE = 503  # Service Unavailable
GATEWAY_TIMEOUT = 504  # Gateway Timeout
HTTP_VERSION_NOT_SUPPORTED = 505  # HTTP Version not supported
VARIANT_ALSO_NEGOTIATES = 506  # Variant Also Negotiates
INSUFFICIENT_STORAGE = 507  # Insufficient Storage
LOOP_DETECTED = 508  # Loop Detected
BANDWIDTH_LIMIT_EXCEEDED = 509  # Bandwidth Limit Exceeded
NOT_EXTENDED = 510  # Not Extended
NETWORK_AUTHENTICATION_REQUIRED = 511  # Network Authentication Required
status_code = {
    100: "Continue",
    101: "Switching Protocols",
    102: "Processing",
    103: "Early Hints",
    103: "Checkpoint",
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    207: "Multi-Status",
    208: "Already Reported",
    226: "IM Used",
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    302: "Moved Temporarily",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    307: "Temporary Redirect",
    308: "Permanent Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Payload Too Large",
    413: "Request Entity Too Large",
    414: "URI Too Long",
    414: "Request-URI Too Long",
    415: "Unsupported Media Type",
    416: "Requested range not satisfiable",
    417: "Expectation Failed",
    418: "I'm a teapot",
    419: "Insufficient Space On Resource",
    420: "Method Failure",
    421: "Destination Locked",
    422: "Unprocessable Entity",
    423: "Locked",
    424: "Failed Dependency",
    425: "Too Early",
    426: "Upgrade Required",
    428: "Precondition Required",
    429: "Too Many Requests",
    431: "Request Header Fields Too Large",
    451: "Unavailable For Legal Reasons",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version not supported",
    506: "Variant Also Negotiates",
    507: "Insufficient Storage",
    508: "Loop Detected",
    509: "Bandwidth Limit Exceeded",
    510: "Not Extended",
    511: "Network Authentication Required",
}
