from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    """
    Register error handlers for the Flask app.
    """
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        response = {
            "error": "Bad Request",
            "message": str(error.description) if hasattr(error, 'description') else "The request could not be understood."
        }
        return jsonify(response), 400

    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors."""
        response = {
            "error": "Unauthorized",
            "message": "Authentication credentials were missing or incorrect."
        }
        return jsonify(response), 401

    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors."""
        response = {
            "error": "Forbidden",
            "message": "You don't have permission to access this resource."
        }
        return jsonify(response), 403

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        response = {
            "error": "Not Found",
            "message": "The requested resource was not found."
        }
        return jsonify(response), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        response = {
            "error": "Method Not Allowed",
            "message": f"The method {error.valid_methods[0] if error.valid_methods else 'unknown'} is not allowed for this resource."
        }
        return jsonify(response), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error."""
        response = {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred."
        }
        return jsonify(response), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all unhandled exceptions."""
        if isinstance(error, HTTPException):
            response = {
                "error": error.name,
                "message": error.description
            }
            return jsonify(response), error.code
        
        # For non-HTTP exceptions, return a 500 error
        response = {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred."
        }
        return jsonify(response), 500


class APIError(Exception):
    """Base class for API errors."""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Convert the error to a dictionary."""
        result = {}
        result['error'] = self.message
        if self.payload:
            result.update(self.payload)
        return result


def handle_api_error(error):
    """Handle APIError exceptions."""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


class ValidationError(APIError):
    """Error raised when input validation fails."""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=400, payload=payload)


class AuthenticationError(APIError):
    """Error raised when authentication fails."""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=401, payload=payload)


class AuthorizationError(APIError):
    """Error raised when authorization fails."""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=403, payload=payload)


class ResourceNotFoundError(APIError):
    """Error raised when a resource is not found."""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=404, payload=payload) 