import os
import asyncio
from imaginepro import ImagineProSDK, ImagineParams, ImagineProSDKOptions

# Get API key from environment variable
api_key = os.environ.get("IMAGINEPRO_API_KEY")
if not api_key:
    raise ValueError("IMAGINEPRO_API_KEY environment variable not set")

# Initialize the SDK
options = ImagineProSDKOptions(
    api_key=api_key,
    base_url="https://api.imaginepro.ai",  # Optional, this is the default
    default_timeout=300,  # Optional, 5 minutes (in seconds)
    fetch_interval=2,  # Optional, 2 seconds
)
sdk = ImagineProSDK(options)

# Basic image generation
def generate_image():
    # Create the parameters for image generation
    params = ImagineParams(
        prompt="a pretty cat playing with a puppy",
    )
    
    try:
        # Start the image generation
        result = sdk.imagine(params)
        print(f"Image generation initiated: {result}")
        
        # Wait for the generation to complete
        message = sdk.fetch_message(result["message_id"])
        print(f"Image generation result: {message}")
        
        # If successful, print the image URL
        if message["status"] == "DONE":
            print(f"Generated image URL: {message.get('uri')}")
        
        return message
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

if __name__ == "__main__":
    generate_image()
