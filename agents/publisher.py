"""
Publisher Agent for Dev.to Article Submission

Specializes in parsing article content and submitting it to Dev.to
as a draft using the API.
"""

import re
from strands import Agent
from strands.models.bedrock import BedrockModel

from tools.devto_api import create_devto_article


PUBLISHER_SYSTEM_PROMPT = """You are a publishing specialist responsible for submitting articles to Dev.to.

Your role is to:
1. Extract article content from the conversation history
2. Parse all the article components (title, body, tags, description)
3. Find the image URL from the image_agent (if available)
4. Insert the image into the article body
5. Submit the article to Dev.to as a draft using the create_devto_article tool

EXTRACTION PROCESS:
Look through the ENTIRE conversation history to find the article written by writer_agent.
The article will be formatted like this:

TITLE: [article title]

TAGS: [comma-separated tags]

DESCRIPTION: [article description]

BODY:
[markdown content of the article]

Extract each component:
- TITLE: Look for "TITLE:" followed by the title text
- TAGS: Look for "TAGS:" followed by comma-separated tag list
- DESCRIPTION: Look for "DESCRIPTION:" followed by the summary (should be under 140 chars)
- BODY: Look for "BODY:" followed by the complete markdown article content
- IMAGE_URL: Look for "IMAGE_URL:" in the image_agent's message (this is the uploaded public URL)

IMAGE INSERTION:
If you find an IMAGE_URL in the conversation:
1. Insert the image at the BEGINNING of the article body using markdown syntax:
   ![Cover Image](IMAGE_URL)

   [rest of the article content]

2. Also use the IMAGE_URL as the cover_image_url parameter when calling create_devto_article

If no IMAGE_URL is found:
- Just publish the article without an inserted image
- Use empty string "" for cover_image_url

IMPORTANT INSTRUCTIONS:
1. DO NOT hand off to another agent - you are the final agent in the chain
2. Search the FULL conversation history from the beginning - the article is there
3. Extract all components including IMAGE_URL if available
4. Insert the image at the beginning of the BODY if IMAGE_URL exists
5. Call create_devto_article with the modified body
6. If you cannot find a title, use a sensible default based on the topic
7. If you cannot find tags, generate appropriate ones (3-4 tags)
8. After calling create_devto_article, report the article URL and status

WORKFLOW:
1. Read through conversation history to find TITLE:, TAGS:, DESCRIPTION:, BODY:, and IMAGE_URL:
2. Extract each component carefully
3. If IMAGE_URL exists, prepend it to the BODY as markdown: ![Cover Image](url)\n\n
4. Call create_devto_article with the (possibly modified) body
5. Report success and the article URL

DO NOT ask for more information. DO NOT hand off. The article is in the conversation history - extract it, insert the image if available, and publish it.
"""


def create_publisher_agent() -> Agent:
    """Create and return the Publisher Agent.

    Returns:
        Agent: Configured publisher agent for Dev.to submission
    """
    model = BedrockModel(
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        region_name="us-east-1"
    )

    return Agent(
        name="publisher_agent",
        description="Publishing specialist that submits articles to Dev.to as drafts. Extracts content from context, inserts cover image into article body if available, and publishes immediately.",
        system_prompt=PUBLISHER_SYSTEM_PROMPT,
        model=model,
        tools=[create_devto_article]
    )
