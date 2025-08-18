"""
Rate limiting module for the API.
Implements rate limiting using a sliding window counter.
"""
from fastapi import HTTPException
from datetime import datetime
from collections import defaultdict
import time
import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

class RateLimiter:
    """Rate limiter implementation using sliding window."""
    
    def __init__(self, requests_per_minute: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum number of requests allowed per minute
        """
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    async def check(self, client_id: str) -> bool:
        """
        Check if request is within rate limits.
        
        Args:
            client_id: Unique identifier for the client (e.g., API key)
            
        Returns:
            bool: True if request is allowed
            
        Raises:
            HTTPException: If rate limit is exceeded
        """
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        if len(self.requests[client_id]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute."
            )
        
        self.requests[client_id].append(now)
        return True
    
    def get_remaining_requests(self, client_id: str) -> int:
        """
        Get number of remaining requests for the client.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            int: Number of remaining requests
        """
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        current_requests = len([
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ])
        
        return max(0, self.requests_per_minute - current_requests)

# Global rate limiter instance
rate_limiter = RateLimiter()
