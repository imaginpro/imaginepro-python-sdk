import unittest
from unittest.mock import patch, MagicMock
import time
import json
import pytest
from typing import Dict, Any

from imaginepro import ImagineProSDK
from imaginepro.types import (
    ImagineProSDKOptions, ImagineParams, ButtonPressParams, UpscaleParams,
    VariantParams, RerollParams, InpaintingParams, BaseParams
)
from imaginepro.constants import Button


class TestImagineProSDK(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test"""
        self.options = ImagineProSDKOptions(
            api_key="test_api_key",
            base_url="https://api.example.com",
            default_timeout=30,
            fetch_interval=1
        )
        
        self.sdk = ImagineProSDK(self.options)
        
        # Common test data
        self.message_id = "test_message_id"
        self.successful_response = {
            "id": self.message_id,
            "message_id": self.message_id,
            "status": "DONE",
            "images": ["image1.png", "image2.png"],
            "progress": 100
        }
        
        self.in_progress_response = {
            "id": self.message_id,
            "message_id": self.message_id,
            "status": "PROCESSING",
            "progress": 50
        }
        
        self.error_response = {
            "error": "Test error message"
        }

    @patch('requests.post')
    def test_imagine(self, mock_post):
        """Test the imagine method"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = self.successful_response
        mock_post.return_value = mock_response
        
        # Call the imagine method
        params = ImagineParams(prompt="a beautiful sunset")
        response = self.sdk.imagine(params)
        
        # Verify the request was made correctly
        mock_post.assert_called_once()
        url = mock_post.call_args[0][0]
        headers = mock_post.call_args[1]['headers']
        json_data = mock_post.call_args[1]['json']
        
        self.assertEqual(url, "https://api.example.com/api/v1/nova/imagine")
        self.assertEqual(headers["Authorization"], "Bearer test_api_key")
        self.assertEqual(json_data["prompt"], "a beautiful sunset")
        
        # Verify the response
        self.assertEqual(response, self.successful_response)
    
    @patch('requests.get')
    def test_fetch_message_once(self, mock_get):
        """Test the fetch_message_once method"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = self.in_progress_response
        mock_get.return_value = mock_response
        
        # Call the fetch_message_once method
        response = self.sdk.fetch_message_once(self.message_id)
        
        # Verify the request was made correctly
        mock_get.assert_called_once()
        url = mock_get.call_args[0][0]
        
        self.assertEqual(url, f"https://api.example.com/api/v1/message/fetch/{self.message_id}")
        
        # Verify the response
        self.assertEqual(response, self.in_progress_response)
    
    @patch('time.sleep', return_value=None)
    @patch('imaginepro.ImagineProSDK.fetch_message_once')
    def test_fetch_message_success(self, mock_fetch_once, mock_sleep):
        """Test the fetch_message method when message completes successfully"""
        # Setup mock responses - first in progress, then done
        mock_fetch_once.side_effect = [
            {"id": self.message_id, "status": "PROCESSING", "progress": 50},
            {"id": self.message_id, "status": "DONE", "images": ["image1.png"]}
        ]
        
        # Call the fetch_message method
        response = self.sdk.fetch_message(self.message_id)
        
        # Verify the mock was called twice and we got the final response
        self.assertEqual(mock_fetch_once.call_count, 2)
        self.assertEqual(response["status"], "DONE")
        self.assertEqual(response["images"], ["image1.png"])
    
    @patch('time.sleep', return_value=None)
    @patch('imaginepro.ImagineProSDK.fetch_message_once')
    def test_fetch_message_timeout(self, mock_fetch_once, mock_sleep):
        """Test the fetch_message method when it times out"""
        # Always return in progress status
        mock_fetch_once.return_value = {"id": self.message_id, "status": "PROCESSING", "progress": 50}
        
        # Mock time.time to simulate timeout
        with patch('time.time') as mock_time:
            mock_time.side_effect = [0, 1, 31]  # Start, first check, second check (timeout)
            
            # Call the fetch_message method with a short timeout
            with self.assertRaises(TimeoutError):
                self.sdk.fetch_message(self.message_id, timeout=30)
    
    @patch('requests.post')
    def test_press_button(self, mock_post):
        """Test the press_button method"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = self.successful_response
        mock_post.return_value = mock_response
        
        # Call the press_button method
        params = ButtonPressParams(
            message_id=self.message_id,
            button=Button.REROLL
        )
        response = self.sdk.press_button(params)
        
        # Verify the request was made correctly
        mock_post.assert_called_once()
        url = mock_post.call_args[0][0]
        json_data = mock_post.call_args[1]['json']
        
        self.assertEqual(url, "https://api.example.com/api/v1/nova/button")
        self.assertEqual(json_data["messageId"], self.message_id)
        self.assertEqual(json_data["button"], Button.REROLL)
        
        # Verify the response
        self.assertEqual(response, self.successful_response)
    
    @patch('imaginepro.ImagineProSDK.press_button')
    def test_upscale(self, mock_press_button):
        """Test the upscale method"""
        # Setup mock response
        mock_press_button.return_value = self.successful_response
        
        # Call the upscale method
        params = UpscaleParams(message_id=self.message_id, index=1)
        response = self.sdk.upscale(params)
        
        # Verify press_button was called with correct params
        mock_press_button.assert_called_once()
        button_params = mock_press_button.call_args[0][0]
        
        self.assertEqual(button_params.message_id, self.message_id)
        self.assertEqual(button_params.button, "U1")
        
        # Verify the response
        self.assertEqual(response, self.successful_response)
    
    @patch('imaginepro.ImagineProSDK.press_button')
    def test_variant(self, mock_press_button):
        """Test the variant method"""
        # Setup mock response
        mock_press_button.return_value = self.successful_response
        
        # Call the variant method
        params = VariantParams(message_id=self.message_id, index=2)
        response = self.sdk.variant(params)
        
        # Verify press_button was called with correct params
        mock_press_button.assert_called_once()
        button_params = mock_press_button.call_args[0][0]
        
        self.assertEqual(button_params.message_id, self.message_id)
        self.assertEqual(button_params.button, "V2")
        
        # Verify the response
        self.assertEqual(response, self.successful_response)
    
    @patch('imaginepro.ImagineProSDK.press_button')
    def test_reroll(self, mock_press_button):
        """Test the reroll method"""
        # Setup mock response
        mock_press_button.return_value = self.successful_response
        
        # Call the reroll method
        params = RerollParams(message_id=self.message_id)
        response = self.sdk.reroll(params)
        
        # Verify press_button was called with correct params
        mock_press_button.assert_called_once()
        button_params = mock_press_button.call_args[0][0]
        
        self.assertEqual(button_params.message_id, self.message_id)
        self.assertEqual(button_params.button, Button.REROLL)
        
        # Verify the response
        self.assertEqual(response, self.successful_response)
    
    @patch('imaginepro.ImagineProSDK.press_button')
    def test_inpainting(self, mock_press_button):
        """Test the inpainting method"""
        # Setup mock response
        mock_press_button.return_value = self.successful_response
        
        # Call the inpainting method
        params = InpaintingParams(
            message_id=self.message_id,
            mask="base64_encoded_mask",
            prompt="add a cat"
        )
        response = self.sdk.inpainting(params)
        
        # Verify press_button was called with correct params
        mock_press_button.assert_called_once()
        button_params = mock_press_button.call_args[0][0]
        
        self.assertEqual(button_params.message_id, self.message_id)
        self.assertEqual(button_params.button, Button.VARY_REGION)
        self.assertEqual(button_params.mask, "base64_encoded_mask")
        self.assertEqual(button_params.prompt, "add a cat")
        
        # Verify the response
        self.assertEqual(response, self.successful_response)
    
    def test_convert_params(self):
        """Test the _convert_params helper method"""
        # Create a test parameter object
        class TestParams:
            def __init__(self):
                self.snake_case_param = "value"
                self.another_param = 123
                self.null_param = None
        
        params = TestParams()
        
        # Call the _convert_params method
        result = self.sdk._convert_params(params)
        
        # Verify the conversion
        self.assertEqual(result, {
            "snakeCaseParam": "value",
            "anotherParam": 123
        })
        
        # Test with non-object parameter
        string_param = "not an object"
        self.assertEqual(self.sdk._convert_params(string_param), "not an object")
    
    def test_extract_base_params(self):
        """Test the _extract_base_params helper method"""
        # Create a test parameter with various base params
        params = BaseParams(
            ref="test_ref",
            webhook_override="https://webhook.example.com",
            timeout=60,
            disable_cdn=True
        )
        
        # Call the _extract_base_params method
        result = self.sdk._extract_base_params(params)
        
        # Verify the result
        expected = {
            "ref": "test_ref",
            "webhookOverride": "https://webhook.example.com",
            "timeout": 60,
            "disableCdn": True
        }
        self.assertEqual(result, expected)
        
        # Test with missing optional params
        minimal_params = BaseParams()
        minimal_result = self.sdk._extract_base_params(minimal_params)
        self.assertEqual(minimal_result, {})

    @patch('requests.post')
    def test_post_request_error(self, mock_post):
        """Test error handling in _post_request method"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.json.return_value = self.error_response
        mock_response.reason = "Bad Request"
        mock_post.return_value = mock_response
        
        # Call the _post_request method
        with self.assertRaises(Exception) as context:
            self.sdk._post_request("/test", {})
        
        # Verify the error message
        self.assertEqual(str(context.exception), "Test error message")


if __name__ == '__main__':
    unittest.main()