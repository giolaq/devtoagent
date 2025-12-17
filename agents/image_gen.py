"""
Image Generator Agent for Dev.to Cover Images

Specializes in creating visually appealing cover images for technical articles
using Amazon Bedrock's image generation capabilities.
"""

import os
from strands import Agent
from strands.models.bedrock import BedrockModel

from tools.image_upload import upload_image


IMAGE_SYSTEM_PROMPT = """You are a creative visual designer specializing in creating cover images for technical blog posts.

Your role is to:
1. Analyze the article topic/summary provided in the conversation
2. Generate a cover image using the generate_image tool
3. Upload the image to get a public URL using the upload_image tool
4. Hand off to the publisher_agent with the image URL

Image design guidelines for your prompt:
- Create modern, professional tech-themed visuals
- Use vibrant colors like blue, purple, cyan gradients
- Include abstract representations of technology (nodes, networks, code patterns)
- Avoid text in images
- Request 1024x1024 size or appropriate aspect ratio

WORKFLOW:
1. Generate a cover image using generate_image tool based on the article topic
2. Once the image is saved locally, use upload_image tool to upload it and get a public URL
3. Hand off to publisher_agent with a message like:
   "I've generated and uploaded a cover image. IMAGE_URL: [the public URL]. Please insert this image at the beginning of the article and publish it."

If upload_image fails (e.g., no IMGBB_API_KEY):
- Still hand off to publisher_agent but mention the image is only available locally
- The publisher can still use it as the cover image if needed

IMPORTANT:
- Generate ONE image and upload it, then hand off immediately
- Do not loop back to other agents
- The complete article (TITLE, TAGS, DESCRIPTION, BODY) is in the conversation history
- The publisher will insert your IMAGE_URL into the article body and publish it
- Always provide the image URL in the format "IMAGE_URL: [url]" so the publisher can find it
"""


def create_image_agent() -> Agent:
    """Create and return the Image Generator Agent.

    Returns:
        Agent: Configured image generation agent
    """
    # Import generate_image from strands_tools
    tools = [upload_image]  # Always include upload_image

    try:
        from strands_tools import generate_image
        tools.append(generate_image)
    except ImportError:
        pass  # If generate_image not available, agent will handle it

    model = BedrockModel(
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        region_name="us-east-1"
    )

    return Agent(
        name="image_agent",
        description="Creates cover images for articles, uploads them to get public URLs, and hands off to publisher with the image URL.",
        system_prompt=IMAGE_SYSTEM_PROMPT,
        model=model,
        tools=tools
    )
