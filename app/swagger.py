swagger_template = {
    "openapi": "3.0.0",
    "info": {
        "title": "Take Your Vitamins API",
        "description": "API for managing vitamin information",
        "version": "1.0"
    },
    "components": {
        "schemas": {
            "Vitamin": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "aliases": {"type": "array", "items": {"type": "string"}},
                    "category": {"type": "string"},
                    "description": {"type": "string"},
                    "intakePractices": {
                        "type": "object",
                        "properties": {
                            "dosage": {"type": "string"},
                            "timing": {"type": "string"},
                            "specialInstructions": {"type": "string"}
                        }
                    },
                    "supplementInteractions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "supplementName": {"type": "string"},
                                "effect": {"type": "string"},
                                "severity": {"type": "string"},
                                "description": {"type": "string"},
                                "recommendation": {"type": "string"}
                            }
                        }
                    },
                    "foodInteractions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "foodName": {"type": "string"},
                                "effect": {"type": "string"},
                                "description": {"type": "string"},
                                "recommendation": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
    },
    "paths": {
        # Vitamin API endpoints have been removed as requested
    }
} 