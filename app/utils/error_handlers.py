from flask import jsonify
from werkzeug.exceptions import HTTPException
import logging
import traceback
import json
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """
    Register error handlers for the Flask app.
    """
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        error_id = log_error(error, level=logging.WARNING)
        response = {
            "error": "Bad Request",
            "message": str(error.description) if hasattr(error, 'description') else "The request could not be understood.",
            "errorId": error_id,
            "statusCode": 400
        }
        return jsonify(response), 400

    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors."""
        error_id = log_error(error, level=logging.WARNING)
        response = {
            "error": "Unauthorized",
            "message": "Authentication credentials were missing or incorrect.",
            "errorId": error_id,
            "statusCode": 401
        }
        return jsonify(response), 401

    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors."""
        error_id = log_error(error, level=logging.WARNING)
        response = {
            "error": "Forbidden",
            "message": "You don't have permission to access this resource.",
            "errorId": error_id,
            "statusCode": 403
        }
        return jsonify(response), 403

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        error_id = log_error(error, level=logging.WARNING)
        response = {
            "error": "Not Found",
            "message": "The requested resource was not found.",
            "errorId": error_id,
            "statusCode": 404
        }
        return jsonify(response), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        error_id = log_error(error, level=logging.WARNING)
        response = {
            "error": "Method Not Allowed",
            "message": f"The method {error.valid_methods[0] if error.valid_methods else 'unknown'} is not allowed for this resource.",
            "errorId": error_id,
            "statusCode": 405
        }
        return jsonify(response), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error."""
        error_id = log_error(error, level=logging.ERROR)
        response = {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred.",
            "errorId": error_id,
            "statusCode": 500
        }
        return jsonify(response), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all unhandled exceptions."""
        if isinstance(error, HTTPException):
            error_id = log_error(error, level=logging.WARNING)
            response = {
                "error": error.name,
                "message": error.description,
                "errorId": error_id,
                "statusCode": error.code
            }
            return jsonify(response), error.code
        
        # For non-HTTP exceptions, return a 500 error
        error_id = log_error(error, level=logging.ERROR)
        response = {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred.",
            "errorId": error_id,
            "statusCode": 500
        }
        return jsonify(response), 500


class APIError(Exception):
    """Base class for API errors."""
    def __init__(self, message, status_code=400, payload=None, details=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload
        self.details = details
        self.error_id = self._generate_error_id()
        
        # Log the error
        self._log_error()

    def to_dict(self):
        """Convert the error to a dictionary."""
        result = {
            "error": self.__class__.__name__,
            "message": self.message,
            "errorId": self.error_id,
            "statusCode": self.status_code
        }
        
        # Include optional details for debugging
        if self.details:
            result["details"] = self.details
            
        # Include additional payload data if provided
        if self.payload:
            result.update(self.payload)
            
        return result
    
    def _generate_error_id(self):
        """Generate a unique error ID for tracking purposes."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}-{unique_id}"
    
    def _log_error(self):
        """Log the error with appropriate severity level."""
        # Determine log level based on status code
        if self.status_code >= 500:
            log_level = logging.ERROR
        elif self.status_code >= 400:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO
            
        log_message = f"[{self.error_id}] {self.__class__.__name__}: {self.message}"
        if self.details:
            log_message += f" - Details: {self.details}"
            
        logger.log(log_level, log_message)


def handle_api_error(error):
    """Handle APIError exceptions."""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


class ValidationError(APIError):
    """Error raised when input validation fails."""
    def __init__(self, message, payload=None, details=None):
        super().__init__(message, status_code=400, payload=payload, details=details)


class AuthenticationError(APIError):
    """Error raised when authentication fails."""
    def __init__(self, message, payload=None, details=None):
        super().__init__(message, status_code=401, payload=payload, details=details)


class PermissionError(APIError):
    """Error raised when a user doesn't have permission to access a resource."""
    def __init__(self, message, payload=None, details=None):
        super().__init__(message, status_code=403, payload=payload, details=details)


class ResourceNotFoundError(APIError):
    """Error raised when a requested resource is not found."""
    def __init__(self, message, payload=None, details=None):
        super().__init__(message, status_code=404, payload=payload, details=details)


class ServerError(APIError):
    """Error raised for server-side errors."""
    def __init__(self, message, payload=None, details=None):
        super().__init__(message, status_code=500, payload=payload, details=details)


def log_error(error, level=logging.ERROR):
    """
    Logs error details and returns a unique error ID for tracking.
    
    Args:
        error: The exception or error object
        level: Logging level to use
        
    Returns:
        str: A unique error ID that can be used for tracking
    """
    # Generate a unique error ID
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    import uuid
    error_id = f"{timestamp}-{str(uuid.uuid4())[:8]}"
    
    # Format error details
    error_type = type(error).__name__
    error_message = str(error)
    error_traceback = traceback.format_exc() if level >= logging.ERROR else None
    
    # Log the error with the unique ID
    logger.log(level, f"[{error_id}] {error_type}: {error_message}")
    
    if error_traceback and error_traceback != "NoneType: None\n":
        logger.log(level, f"[{error_id}] Traceback: {error_traceback}")
    
    return error_id 