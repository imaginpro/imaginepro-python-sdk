from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union, TypedDict, Literal

# Base Parameter Types
@dataclass
class BaseParams:
    ref: Optional[str] = None  # Reference id which will be sent to webhook
    webhook_override: Optional[str] = None  # Webhook URL for receiving generation result callbacks
    timeout: Optional[int] = None  # Timeout in seconds
    disable_cdn: Optional[bool] = None  # Whether to disable CDN


@dataclass
class ImagineParams(BaseParams):
    prompt: str


@dataclass
class ButtonPressParams(BaseParams):
    message_id: str  # Unique identifier for the message
    button: str  # Button identifier (e.g., "U1")
    mask: Optional[str] = None  # Optional mask for the Vary Region action
    prompt: Optional[str] = None  # Optional prompt for the Vary Region action


@dataclass
class UpscaleParams(BaseParams):
    message_id: str  # Unique identifier for the message
    index: int  # Index of the button to upscale


@dataclass
class VariantParams(BaseParams):
    message_id: str  # Unique identifier for the message
    index: int  # Index of the button to generate a variant


@dataclass
class RerollParams(BaseParams):
    message_id: str  # Unique identifier for the message


@dataclass
class InpaintingParams(BaseParams):
    message_id: str  # Unique identifier for the message
    mask: str  # Mask for the region to vary, required
    prompt: Optional[str] = None  # Optional prompt for the inpainting


# Response Types
class ImagineResponse(TypedDict):
    message_id: str  # Unique identifier for the image generation task
    success: Literal['PROCESSING', 'QUEUED', 'DONE', 'FAIL']  # Task status
    created_at: Optional[str]  # If the task is completed, returns the created timestamp
    error: Optional[str]  # If the task fails, returns the error message


class ErrorResponse(TypedDict):
    message: str  # Error message
    error: Optional[str]  # Detailed error information
    status_code: int  # HTTP status code


class MessageResponse(TypedDict):
    message_id: str  # Unique identifier for the message
    prompt: str  # The prompt used for image generation
    original_url: Optional[str]  # Original image URL
    uri: Optional[str]  # Generated image URL
    progress: int  # Progress percentage
    status: Literal['PROCESSING', 'QUEUED', 'DONE', 'FAIL']  # Current status of the message
    created_at: Optional[str]  # Creation timestamp
    updated_at: Optional[str]  # Last update timestamp
    buttons: Optional[List[str]]  # Available action buttons
    originating_message_id: Optional[str]  # ID of the originating message
    ref: Optional[str]  # Reference information
    error: Optional[str]  # If the task fails, returns the error message


# Configuration
@dataclass
class ImagineProSDKOptions:
    api_key: str  # API key for authentication
    base_url: str = "https://api.imaginepro.ai"  # Base URL for the API
    default_timeout: int = 1800  # Default timeout for requests in seconds (30 minutes)
    fetch_interval: int = 2  # Interval for polling the message status in seconds