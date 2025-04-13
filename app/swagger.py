from flask_swagger_ui import get_swaggerui_blueprint

# Create Swagger UI blueprint
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Take Your Vitamins API"
    }
)

# Swagger JSON template
swagger_template = {
    "openapi": "3.0.0",
    "info": {
        "title": "Take Your Vitamins API",
        "description": "API for managing supplements, health logs, and user profiles",
        "version": "1.0",
        "contact": {
            "name": "Development Team",
            "email": "dev@takeyourvitamins.com"
        }
    },
    "servers": [
        {
            "url": "/",
            "description": "Main server"
        }
    ],
    "components": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        },
        "schemas": {
            "User": {
                "type": "object",
                "properties": {
                    "userId": {"type": "string", "description": "Unique identifier for the user"},
                    "name": {"type": "string", "description": "User's full name"},
                    "email": {"type": "string", "format": "email", "description": "User's email address"},
                    "age": {"type": "integer", "description": "User's age"},
                    "gender": {"type": "string", "description": "User's gender"},
                    "createdAt": {"type": "string", "format": "date-time", "description": "Timestamp when the user was created"},
                    "updatedAt": {"type": "string", "format": "date-time", "description": "Timestamp when the user was last updated"},
                    "deletedAt": {"type": "string", "format": "date-time", "description": "Timestamp when the user was deleted, if applicable"}
                }
            },
            "Supplement": {
                "type": "object",
                "properties": {
                    "supplementId": {"type": "string", "description": "Unique identifier for the supplement"},
                    "name": {"type": "string", "description": "Name of the supplement"},
                    "aliases": {"type": "array", "items": {"type": "string"}, "description": "Alternative names for the supplement"},
                    "category": {"type": "string", "description": "Category of the supplement (vitamin, mineral, herb, etc.)"},
                    "description": {"type": "string", "description": "Description of the supplement"},
                    "dosageInfo": {"type": "string", "description": "General dosage information"},
                    "createdAt": {"type": "string", "format": "date-time", "description": "Timestamp when the supplement was created"},
                    "updatedAt": {"type": "string", "format": "date-time", "description": "Timestamp when the supplement was last updated"}
                }
            },
            "IntakeLog": {
                "type": "object",
                "properties": {
                    "logId": {"type": "string", "description": "Unique identifier for the intake log"},
                    "userId": {"type": "string", "description": "ID of the user who took the supplement"},
                    "supplementId": {"type": "string", "description": "ID of the supplement that was taken"},
                    "timestamp": {"type": "string", "format": "date-time", "description": "When the supplement was taken"},
                    "dosage": {"type": "string", "description": "Dosage that was taken"},
                    "notes": {"type": "string", "description": "Any notes about the intake"},
                    "createdAt": {"type": "string", "format": "date-time", "description": "Timestamp when the log was created"}
                }
            },
            "SymptomLog": {
                "type": "object",
                "properties": {
                    "logId": {"type": "string", "description": "Unique identifier for the symptom log"},
                    "userId": {"type": "string", "description": "ID of the user who experienced the symptom"},
                    "symptom": {"type": "string", "description": "The symptom experienced"},
                    "severity": {"type": "integer", "description": "Severity of the symptom (1-10)"},
                    "timestamp": {"type": "string", "format": "date-time", "description": "When the symptom was experienced"},
                    "notes": {"type": "string", "description": "Any notes about the symptom"},
                    "createdAt": {"type": "string", "format": "date-time", "description": "Timestamp when the log was created"}
                }
            },
            "Interaction": {
                "type": "object",
                "properties": {
                    "interactionId": {"type": "string", "description": "Unique identifier for the interaction"},
                    "supplement1Id": {"type": "string", "description": "ID of the first supplement"},
                    "supplement2Id": {"type": "string", "description": "ID of the second supplement"},
                    "interactionType": {"type": "string", "description": "Type of interaction (enhancing, inhibiting, etc.)"},
                    "severity": {"type": "string", "enum": ["low", "medium", "high"], "description": "Severity of the interaction"},
                    "description": {"type": "string", "description": "Description of the interaction"},
                    "recommendation": {"type": "string", "description": "Recommendations regarding this interaction"},
                    "createdAt": {"type": "string", "format": "date-time", "description": "Timestamp when the interaction was created"},
                    "updatedAt": {"type": "string", "format": "date-time", "description": "Timestamp when the interaction was last updated"}
                }
            },
            "Alert": {
                "type": "object",
                "properties": {
                    "alertId": {"type": "string", "description": "Unique identifier for the alert"},
                    "userId": {"type": "string", "description": "ID of the user the alert is for"},
                    "type": {"type": "string", "description": "Type of alert"},
                    "message": {"type": "string", "description": "Alert message"},
                    "read": {"type": "boolean", "description": "Whether the alert has been read"},
                    "createdAt": {"type": "string", "format": "date-time", "description": "Timestamp when the alert was created"}
                }
            },
            "AuthResponse": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Status message"},
                    "userId": {"type": "string", "description": "ID of the authenticated user"},
                    "access_token": {"type": "string", "description": "JWT access token"}
                }
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "description": "Error message"}
                }
            }
        }
    },
    "paths": {
        "/api/auth/register": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Register a new user",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["name", "email", "password", "age", "gender"],
                                "properties": {
                                    "name": {"type": "string"},
                                    "email": {"type": "string", "format": "email"},
                                    "password": {"type": "string", "format": "password"},
                                    "age": {"type": "integer"},
                                    "gender": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "User registered successfully",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AuthResponse"}
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid input or email already exists",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                }
            }
        },
        "/api/auth/login": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Login with email and password",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["email", "password"],
                                "properties": {
                                    "email": {"type": "string", "format": "email"},
                                    "password": {"type": "string", "format": "password"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Login successful",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AuthResponse"}
                            }
                        }
                    },
                    "401": {
                        "description": "Invalid email or password",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                }
            }
        },
        "/api/auth/me": {
            "get": {
                "tags": ["Authentication"],
                "summary": "Get current user information",
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "User information retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            }
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    },
                    "404": {
                        "description": "User not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                }
            }
        },
        "/api/users/": {
            "get": {
                "tags": ["Users"],
                "summary": "Get user profile",
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "User profile retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            }
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    },
                    "404": {
                        "description": "User not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                }
            },
            "put": {
                "tags": ["Users"],
                "summary": "Update user profile",
                "security": [{"bearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "age": {"type": "integer"},
                                    "gender": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Profile updated successfully",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            }
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    },
                    "501": {
                        "description": "Not implemented",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                }
            }
        },
        "/api/supplements/": {
            "get": {
                "tags": ["Supplements"],
                "summary": "Get a list of supplements",
                "responses": {
                    "200": {
                        "description": "List of supplements",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Supplement"}
                                }
                            }
                        }
                    },
                    "501": {
                        "description": "Not implemented",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                }
            }
        },
        "/api/intake-logs/": {
            "get": {
                "tags": ["Intake Logs"],
                "summary": "Get a list of intake logs",
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "List of intake logs",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/IntakeLog"}
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    },
                    "501": {
                        "description": "Not implemented",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                }
            }
        },
        "/api/symptom-logs/": {
            "get": {
                "tags": ["Symptom Logs"],
                "summary": "Get a list of symptom logs",
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "List of symptom logs",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/SymptomLog"}
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    },
                    "501": {
                        "description": "Not implemented",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                }
            }
        },
        "/api/interactions/": {
            "get": {
                "tags": ["Interactions"],
                "summary": "Get a list of supplement interactions",
                "responses": {
                    "200": {
                        "description": "List of interactions",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Interaction"}
                                }
                            }
                        }
                    },
                    "501": {
                        "description": "Not implemented",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                }
            }
        },
        "/api/alerts/": {
            "get": {
                "tags": ["Alerts"],
                "summary": "Get a list of alerts",
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "List of alerts",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Alert"}
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    },
                    "501": {
                        "description": "Not implemented",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                }
            }
        }
    }
} 