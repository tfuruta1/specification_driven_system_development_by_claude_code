#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Error Handling - Extracted from error_handler.py
Standard error classes and core error handling functionality

Split from original error_handler.py (636 lines) following single responsibility principle
Focus: Error class definitions, basic error handling, error categorization
"""

import traceback
import json
from datetime import datetime
import copy
from pathlib import Path
from typing import Optional, Dict, Any, Union
from enum import Enum


class ErrorSeverity(Enum):
    """ERROR"""
    CRITICAL = "critical"    # ERROR
    HIGH = "high"           # 
    MEDIUM = "medium"       # ERROR
    LOW = "low"            # ERROR
    INFO = "info"          # ERROR


class ErrorCategory(Enum):
    """ERROR"""
    FILE_OPERATION = "file_operation"
    VALIDATION = "validation"
    NETWORK = "network"
    CONFIGURATION = "configuration"
    PERMISSION = "permission"
    RESOURCE = "resource"
    BUSINESS_LOGIC = "business_logic"
    SYSTEM = "system"


class StandardError(Exception):
    """ERROR"""
    
    def __init__(self, message: str, error_code: str = None,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 category: ErrorCategory = ErrorCategory.SYSTEM,
                 details: Optional[Dict] = None,
                 original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.category = category
        self.details = details or {}
        self.original_exception = original_exception
        self.timestamp = datetime.now()
        self.traceback_info = traceback.format_exc() if original_exception else None
    
    def to_dict(self) -> Dict[str, Any]:
        """ERROR"""
        return {
            'message': self.message,
            'error_code': self.error_code,
            'severity': self.severity.value,
            'category': self.category.value,
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
            'has_original_exception': self.original_exception is not None,
            'has_traceback': self.traceback_info is not None
        }
    
    def to_json(self) -> str:
        """JSON"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class FileOperationError(StandardError):
    """ERROR"""
    
    def __init__(self, message: str, file_path: Union[str, Path] = None, **kwargs):
        super().__init__(message, category=ErrorCategory.FILE_OPERATION, **kwargs)
        self.file_path = str(file_path) if file_path else None
        if self.file_path:
            self.details['file_path'] = self.file_path


class ValidationError(StandardError):
    """ERROR"""
    
    def __init__(self, message: str, field_name: str = None, 
                 invalid_value: Any = None, **kwargs):
        super().__init__(message, category=ErrorCategory.VALIDATION, **kwargs)
        self.field_name = field_name
        self.invalid_value = invalid_value
        if field_name:
            self.details['field_name'] = field_name
        if invalid_value is not None:
            self.details['invalid_value'] = str(invalid_value)


class NetworkError(StandardError):
    """ERROR"""
    
    def __init__(self, message: str, url: str = None, status_code: int = None, **kwargs):
        super().__init__(message, category=ErrorCategory.NETWORK, **kwargs)
        self.url = url
        self.status_code = status_code
        if url:
            self.details['url'] = url
        if status_code:
            self.details['status_code'] = status_code


class ConfigurationError(StandardError):
    """ERROR"""
    
    def __init__(self, message: str, config_key: str = None, 
                 config_file: Union[str, Path] = None, **kwargs):
        super().__init__(message, category=ErrorCategory.CONFIGURATION, **kwargs)
        self.config_key = config_key
        self.config_file = str(config_file) if config_file else None
        if config_key:
            self.details['config_key'] = config_key
        if self.config_file:
            self.details['config_file'] = self.config_file


class PermissionError(StandardError):
    """ERROR"""
    
    def __init__(self, message: str, resource: str = None, 
                 required_permission: str = None, **kwargs):
        super().__init__(message, category=ErrorCategory.PERMISSION, **kwargs)
        self.resource = resource
        self.required_permission = required_permission
        if resource:
            self.details['resource'] = resource
        if required_permission:
            self.details['required_permission'] = required_permission


class ResourceError(StandardError):
    """ERROR"""
    
    def __init__(self, message: str, resource_type: str = None, 
                 resource_limit: Any = None, current_usage: Any = None, **kwargs):
        super().__init__(message, category=ErrorCategory.RESOURCE, **kwargs)
        self.resource_type = resource_type
        self.resource_limit = resource_limit
        self.current_usage = current_usage
        if resource_type:
            self.details['resource_type'] = resource_type
        if resource_limit is not None:
            self.details['resource_limit'] = str(resource_limit)
        if current_usage is not None:
            self.details['current_usage'] = str(current_usage)


class BusinessLogicError(StandardError):
    """ERROR"""
    
    def __init__(self, message: str, business_rule: str = None, **kwargs):
        super().__init__(message, category=ErrorCategory.BUSINESS_LOGIC, **kwargs)
        self.business_rule = business_rule
        if business_rule:
            self.details['business_rule'] = business_rule


class ErrorFactory:
    """ERROR"""
    
    ERROR_TYPE_MAP = {
        ErrorCategory.FILE_OPERATION: FileOperationError,
        ErrorCategory.VALIDATION: ValidationError,
        ErrorCategory.NETWORK: NetworkError,
        ErrorCategory.CONFIGURATION: ConfigurationError,
        ErrorCategory.PERMISSION: PermissionError,
        ErrorCategory.RESOURCE: ResourceError,
        ErrorCategory.BUSINESS_LOGIC: BusinessLogicError,
        ErrorCategory.SYSTEM: StandardError
    }
    
    @classmethod
    def create_error(cls, category: ErrorCategory, message: str, **kwargs) -> StandardError:
        """ERROR"""
        error_class = cls.ERROR_TYPE_MAP.get(category, StandardError)
        return error_class(message, **kwargs)
    
    @classmethod
    def from_exception(cls, exception: Exception, 
                      category: ErrorCategory = ErrorCategory.SYSTEM,
                      additional_message: str = None) -> StandardError:
        """ERROR StandardError ERROR"""
        message = additional_message or str(exception)
        return cls.create_error(
            category=category,
            message=message,
            original_exception=exception,
            severity=ErrorSeverity.HIGH
        )


# ERROR
def create_file_error(message: str, file_path: Union[str, Path] = None, **kwargs) -> FileOperationError:
    """ERROR"""
    return FileOperationError(message, file_path=file_path, **kwargs)


def create_validation_error(message: str, field_name: str = None, 
                          invalid_value: Any = None, **kwargs) -> ValidationError:
    """ERROR"""
    return ValidationError(message, field_name=field_name, 
                         invalid_value=invalid_value, **kwargs)


def create_network_error(message: str, url: str = None, 
                        status_code: int = None, **kwargs) -> NetworkError:
    """ERROR"""
    return NetworkError(message, url=url, status_code=status_code, **kwargs)


def create_config_error(message: str, config_key: str = None, 
                       config_file: Union[str, Path] = None, **kwargs) -> ConfigurationError:
    """ERROR"""
    return ConfigurationError(message, config_key=config_key, 
                            config_file=config_file, **kwargs)