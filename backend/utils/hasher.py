"""
Content hashing utilities for cache key generation
"""
import hashlib
from typing import Optional


def generate_cache_key(
    llm_provider: str,
    agent_name: str,
    content: str,
    hash_length: int = 16
) -> str:
    """
    Generate a deterministic cache key based on content hash

    Args:
        llm_provider: LLM provider name (gemini/claude)
        agent_name: Agent name (linguistic/structural/etc)
        content: The discharge summary content to hash
        hash_length: Length of hash to use (default: 16 characters)

    Returns:
        Cache key in format: {llm_provider}:{agent_name}:{content_hash}

    Example:
        >>> generate_cache_key("gemini", "linguistic", "Patient data...")
        "gemini:linguistic:a3f5d8c2e1b4f9a7"
    """
    # Generate SHA-256 hash of the content
    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:hash_length]

    # Combine provider, agent, and content hash
    cache_key = f"{llm_provider}:{agent_name}:{content_hash}"

    return cache_key


def hash_content(content: str, algorithm: str = "sha256") -> str:
    """
    Generate hash of content using specified algorithm

    Args:
        content: Content to hash
        algorithm: Hash algorithm (sha256, sha1, md5)

    Returns:
        Hexadecimal hash string
    """
    if algorithm == "sha256":
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(content.encode('utf-8')).hexdigest()
    elif algorithm == "md5":
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")


def verify_cache_key(cache_key: str) -> bool:
    """
    Verify that a cache key has the correct format

    Args:
        cache_key: Cache key to verify

    Returns:
        True if valid format
    """
    parts = cache_key.split(":")
    return len(parts) == 3 and all(parts)
