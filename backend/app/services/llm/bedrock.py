"""
Le Sésame Backend - AWS Bedrock LLM Provider

LangChain wrapper for AWS Bedrock.

Author: Petros Raptopoulos
Date: 2026/02/07
"""

from langchain_aws import ChatBedrock

from ...core import logger


def get_bedrock_llm(
    model_id: str,
    aws_access_key_id: str,
    aws_secret_access_key: str,
    region_name: str,
    **kwargs
):
    """
    Returns an instance of AWS Bedrock LLM with additional parameters.

    Args:
        model_id (str): The Bedrock model ID to use.
        aws_access_key_id (str): AWS access key ID.
        aws_secret_access_key (str): AWS secret access key.
        region_name (str): AWS region name.
        **kwargs: Additional arguments (e.g., max_tokens, temperature).

    Returns:
        ChatBedrock: Configured instance of AWS Bedrock LLM.
    """
    if not aws_access_key_id or not aws_secret_access_key:
        logger.warning("AWS credentials not provided")
        return None
    
    return ChatBedrock(
        model_id=model_id,
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        beta_use_converse_api=True,
        **kwargs
    )
