"""
New Relic GraphQL API client with retry logic and error handling.

This module provides a robust API client for New Relic's NerdGraph API,
handling authentication, request retries for transient errors, and fail-fast
behavior for rate limits and authorization failures.
"""

import requests
import time
import logging
import json
import os
import glob
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class ApiClient:
    """
    New Relic GraphQL API client with retry logic and error handling.
    
    Handles authentication, request retries for transient errors,
    and fail-fast behavior for rate limits and authorization failures.
    """
    
    def __init__(
        self, 
        api_key: str, 
        account_id: str, 
        timeout: int = 30, 
        max_retries: int = 2, 
        retry_delay: int = 5
    ):
        """
        Initialize API client with credentials and configuration.
        
        Args:
            api_key: New Relic User API Key (NRAK-...)
            account_id: New Relic account ID
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum retry attempts (default: 2)
            retry_delay: Delay between retries in seconds (default: 5)
        """
        self._api_key = api_key
        self._account_id = account_id
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._endpoint = "https://api.newrelic.com/graphql"
        self._logger = logging.getLogger('api_client')
    
    def _safe_float(self, value):
        """Convert value to float, return None if conversion fails or value is None."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value):
        """Convert value to int, return None if conversion fails or value is None."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def _make_request(
        self, 
        query: str, 
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute GraphQL query against New Relic API with retry logic.
        
        Args:
            query: GraphQL query string
            variables: Optional query variables
            
        Returns:
            Parsed JSON response from API
            
        Raises:
            requests.exceptions.HTTPError: For 4xx/5xx errors after retries
            requests.exceptions.Timeout: After exhausting retries
            ValueError: For rate limit (429) errors, authentication failures, or GraphQL errors
        """
        # Validate input
        if not query or not query.strip():
            raise ValueError("GraphQL query cannot be empty")
        
        headers = {
            'Authorization': f'Bearer {self._api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'query': query
        }
        if variables:
            payload['variables'] = variables
        
        # Retry loop for transient errors
        last_error = None
        for attempt in range(self._max_retries + 1):  # +1 for initial attempt
            try:
                start_time = time.time()
                
                response = requests.post(
                    self._endpoint,
                    json=payload,
                    headers=headers,
                    timeout=self._timeout
                )
                
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Handle rate limiting (fail fast, no retry)
                if response.status_code == 429:
                    reset_time = response.headers.get('X-RateLimit-Reset', 'unknown')
                    error_msg = f"New Relic API rate limit exceeded. Reset time: {reset_time}. Wait before making more requests."
                    self._logger.error(f"[ERROR] [api_client] {error_msg}")
                    raise ValueError(error_msg)
                
                # Handle authentication errors (fail fast, no retry)
                if response.status_code in (401, 403):
                    error_msg = "Invalid New Relic API key or insufficient permissions. Verify api_key in configuration."
                    self._logger.error(f"[ERROR] [api_client] {error_msg}")
                    raise ValueError(error_msg)
                
                # Raise for other 4xx/5xx errors (will retry on 5xx)
                response.raise_for_status()
                
                # Success - log and validate response
                self._logger.info(f"[INFO] [api_client] Request completed in {duration_ms}ms")
                self._logger.debug(
                    f"[DEBUG] [api_client] Response status: {response.status_code}, "
                    f"Response size: {len(response.content)} bytes"
                )
                
                # Parse and validate GraphQL response
                json_response = response.json()
                
                # Check for GraphQL errors (can occur even with HTTP 200)
                if 'errors' in json_response and json_response['errors']:
                    errors = json_response['errors']
                    error_msg = f"GraphQL errors: {errors}"
                    self._logger.error(f"[ERROR] [api_client] {error_msg}")
                    raise ValueError(error_msg)
                
                return json_response
                
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                # Transient network errors - retry
                last_error = e
                if attempt < self._max_retries:
                    self._logger.warning(
                        f"[WARNING] [api_client] Retry {attempt + 1}/{self._max_retries} "
                        f"after error: {type(e).__name__}: {str(e)}"
                    )
                    time.sleep(self._retry_delay)
                    continue
                    
            except requests.exceptions.HTTPError as e:
                # HTTP errors
                if e.response.status_code >= 500:
                    # Server errors - retry
                    last_error = e
                    if attempt < self._max_retries:
                        self._logger.warning(
                            f"[WARNING] [api_client] Retry {attempt + 1}/{self._max_retries} "
                            f"after error: HTTP {e.response.status_code}"
                        )
                        time.sleep(self._retry_delay)
                        continue
                # Client errors (4xx) - fail fast, no retry
                error_msg = f"API request failed with HTTP {e.response.status_code}: {str(e)}"
                self._logger.error(f"[ERROR] [api_client] {error_msg}")
                raise
        
        # Retries exhausted
        error_msg = (
            f"API request failed after {self._max_retries} retries. "
            f"Last error: {type(last_error).__name__}: {str(last_error)}. "
            f"Check logs for details or try again later."
        )
        self._logger.error(f"[ERROR] [api_client] {error_msg}")
        
        # Create HTTPError with proper response context
        http_error = requests.exceptions.HTTPError(error_msg)
        # Attach the last error for debugging context
        http_error.__cause__ = last_error
        raise http_error
    
    def fetch_performance_metrics(
        self, 
        app_id: str, 
        days: int
    ) -> Dict[str, Any]:
        """
        Fetch performance metrics for a specific application.
        
        Retrieves response time (ms), throughput (rpm), and Apdex score
        for the specified time window.
        
        Args:
            app_id: New Relic application ID
            days: Time window in days (must be 3, 7, 14, or 30)
            
        Returns:
            Dictionary with structure:
            {
                "app_id": str,
                "timestamp": str (ISO 8601),
                "performance": {
                    "response_time": float or None (milliseconds),
                    "throughput": float or None (requests per minute),
                    "apdex_score": float or None (0.0 to 1.0)
                }
            }
            
        Raises:
            ValueError: If app_id is empty or days not in [3, 7, 14, 30]
            requests.exceptions.*: For API request failures
        """
        from datetime import datetime, timedelta
        
        # Validate app_id
        if not app_id or not app_id.strip():
            raise ValueError("app_id cannot be empty")
        
        # Validate days parameter
        ALLOWED_DAYS = [3, 7, 14, 30]
        if days not in ALLOWED_DAYS:
            raise ValueError(f"days must be one of {ALLOWED_DAYS}, got {days}")
        
        # Calculate time window (since timestamp)
        since = datetime.utcnow() - timedelta(days=days)
        since_iso = since.isoformat() + 'Z'  # Add 'Z' for UTC
        
        # Construct NerdGraph NRQL query for performance metrics
        # Note: NRQL string must have values injected via f-string, not GraphQL variables
        nrql_query = f"SELECT average(duration) as 'average.duration', rate(count(*), 1 minute) as 'rate', apdex(duration) as 'apdex' FROM Transaction WHERE appId = '{app_id}' SINCE '{since_iso}'"
        
        query = f"""
        query($accountId: Int!) {{
          actor {{
            account(id: $accountId) {{
              nrql(query: "{nrql_query}") {{
                results
              }}
            }}
          }}
        }}
        """
        
        variables = {
            'accountId': int(self._account_id)
        }
        
        try:
            # Make API request
            self._logger.debug(
                f"[DEBUG] [api_client] Fetching performance metrics: "
                f"app_id={app_id}, days={days}, since={since_iso}"
            )
            
            response = self._make_request(query, variables)
            
            # Extract metrics from response
            results = response.get('data', {}).get('actor', {}).get('account', {}).get('nrql', {}).get('results', [])
            
            if not results:
                # No data available
                metrics = {
                    'response_time': None,
                    'throughput': None,
                    'apdex_score': None
                }
            else:
                result = results[0]
                # Convert all values to float (handles strings from API)
                metrics = {
                    'response_time': self._safe_float(result.get('average.duration')),  # milliseconds
                    'throughput': self._safe_float(result.get('rate')),  # requests per minute
                    'apdex_score': self._safe_float(result.get('apdex'))  # 0.0 to 1.0
                }
            
            # Generate current timestamp with UTC indicator
            timestamp = datetime.utcnow().isoformat() + 'Z'
            
            # Build response dictionary
            response_dict = {
                'app_id': app_id,
                'timestamp': timestamp,
                'performance': metrics
            }
            
            # Log success
            self._logger.info(
                f"[INFO] [api_client] Fetched performance metrics for app_id={app_id}, days={days}"
            )
            
            return response_dict
            
        except Exception as e:
            # Log error with context
            error_msg = f"Failed to fetch performance metrics: {type(e).__name__}: {str(e)}"
            self._logger.error(
                f"[ERROR] [api_client] {error_msg}. app_id={app_id}, days={days}"
            )
            # Re-raise original exception
            raise
    
    def fetch_error_metrics(
        self, 
        app_id: str, 
        days: int
    ) -> Dict[str, Any]:
        """
        Fetch error metrics for a specific application.
        
        Retrieves error rate (as decimal), error count, and error types
        for the specified time window.
        
        Args:
            app_id: New Relic application ID
            days: Time window in days (must be 3, 7, 14, or 30)
            
        Returns:
            Dictionary with structure:
            {
                "app_id": str,
                "timestamp": str (ISO 8601),
                "errors": {
                    "error_rate": float or None (0.0 to 1.0, decimal not percentage),
                    "error_count": int or None,
                    "error_types": list of str or None
                }
            }
            
        Raises:
            ValueError: If app_id is empty or days not in [3, 7, 14, 30]
            requests.exceptions.*: For API request failures
        """
        from datetime import datetime, timedelta
        
        # Validate app_id
        if not app_id or not app_id.strip():
            raise ValueError("app_id cannot be empty")
        
        # Validate days parameter
        ALLOWED_DAYS = [3, 7, 14, 30]
        if days not in ALLOWED_DAYS:
            raise ValueError(f"days must be one of {ALLOWED_DAYS}, got {days}")
        
        # Calculate time window (since timestamp)
        since = datetime.utcnow() - timedelta(days=days)
        since_iso = since.isoformat() + 'Z'  # Add 'Z' for UTC
        
        # Construct NerdGraph NRQL query for error metrics
        # Note: NRQL string must have values injected via f-string, not GraphQL variables
        nrql_query = f"SELECT percentage(count(*), WHERE error IS true) as 'error.rate', count(*) FILTER(WHERE error IS true) as 'error.count', uniques(error.class) as 'error.types' FROM Transaction WHERE appId = '{app_id}' SINCE '{since_iso}'"
        
        query = f"""
        query($accountId: Int!) {{
          actor {{
            account(id: $accountId) {{
              nrql(query: "{nrql_query}") {{
                results
              }}
            }}
          }}
        }}
        """
        
        variables = {
            'accountId': int(self._account_id)
        }
        
        try:
            # Make API request
            self._logger.debug(
                f"[DEBUG] [api_client] Fetching error metrics: "
                f"app_id={app_id}, days={days}, since={since_iso}"
            )
            
            response = self._make_request(query, variables)
            
            # Extract metrics from response
            results = response.get('data', {}).get('actor', {}).get('account', {}).get('nrql', {}).get('results', [])
            
            if not results:
                # No data available
                metrics = {
                    'error_rate': None,
                    'error_count': None,
                    'error_types': None
                }
            else:
                result = results[0]
                
                # Convert error rate from percentage to decimal (5.0 -> 0.05)
                error_rate_pct = self._safe_float(result.get('error.rate'))
                error_rate = (error_rate_pct / 100.0) if error_rate_pct is not None else None
                
                # Convert error count to int
                error_count = self._safe_int(result.get('error.count'))
                
                # Parse error types (may be array or comma-separated string)
                error_types_raw = result.get('error.types')
                if error_types_raw is None:
                    error_types = None
                elif isinstance(error_types_raw, list):
                    error_types = [str(t) for t in error_types_raw if t]
                elif isinstance(error_types_raw, str):
                    # Handle comma-separated string
                    error_types = [t.strip() for t in error_types_raw.split(',') if t.strip()]
                else:
                    error_types = None
                
                metrics = {
                    'error_rate': error_rate,
                    'error_count': error_count,
                    'error_types': error_types
                }
            
            # Generate current timestamp with UTC indicator
            timestamp = datetime.utcnow().isoformat() + 'Z'
            
            # Build response dictionary
            response_dict = {
                'app_id': app_id,
                'timestamp': timestamp,
                'errors': metrics
            }
            
            # Log success
            self._logger.info(
                f"[INFO] [api_client] Fetched error metrics for app_id={app_id}, days={days}"
            )
            
            return response_dict
            
        except Exception as e:
            # Log error with context
            error_msg = f"Failed to fetch error metrics: {type(e).__name__}: {str(e)}"
            self._logger.error(
                f"[ERROR] [api_client] {error_msg}. app_id={app_id}, days={days}"
            )
            # Re-raise original exception
            raise
    
    def fetch_infrastructure_metrics(
        self, 
        app_id: str, 
        days: int
    ) -> Dict[str, Any]:
        """
        Fetch infrastructure metrics for a specific application.
        
        Retrieves CPU usage, memory usage, and disk I/O
        for the specified time window.
        
        Args:
            app_id: New Relic application ID
            days: Time window in days (must be 3, 7, 14, or 30)
            
        Returns:
            Dictionary with structure:
            {
                "app_id": str,
                "timestamp": str (ISO 8601),
                "infrastructure": {
                    "cpu_usage": float or None (0.0 to 1.0),
                    "memory_usage": float or None (0.0 to 1.0),
                    "disk_io": float or None (MB/s)
                }
            }
            
        Raises:
            ValueError: If app_id is empty or days not in [3, 7, 14, 30]
            requests.exceptions.*: For API request failures
        """
        # Validate app_id
        if not app_id or not app_id.strip():
            raise ValueError("app_id cannot be empty")
        
        # Validate days parameter
        ALLOWED_DAYS = [3, 7, 14, 30]
        if days not in ALLOWED_DAYS:
            raise ValueError(f"days must be one of {ALLOWED_DAYS}, got {days}")
        
        # Calculate time window (since timestamp)
        since = datetime.utcnow() - timedelta(days=days)
        since_iso = since.isoformat() + 'Z'  # Add 'Z' for UTC
        
        # Construct NerdGraph NRQL query for infrastructure metrics
        # Note: NRQL string must have values injected via f-string, not GraphQL variables
        nrql_query = f"SELECT average(cpuPercent) as 'cpu.usage', average(memoryUsedPercent) as 'memory.usage', average(diskReadBytesPerSecond + diskWriteBytesPerSecond) / 1024 / 1024 as 'disk.io' FROM SystemSample WHERE appId = '{app_id}' SINCE '{since_iso}'"
        
        query = f"""
        query($accountId: Int!) {{
          actor {{
            account(id: $accountId) {{
              nrql(query: "{nrql_query}") {{
                results
              }}
            }}
          }}
        }}
        """
        
        variables = {
            'accountId': int(self._account_id)
        }
        
        try:
            # Make API request
            self._logger.debug(
                f"[DEBUG] [api_client] Fetching infrastructure metrics: "
                f"app_id={app_id}, days={days}, since={since_iso}"
            )
            
            response = self._make_request(query, variables)
            
            # Extract metrics from response
            results = response.get('data', {}).get('actor', {}).get('account', {}).get('nrql', {}).get('results', [])
            
            if not results:
                # No data available
                metrics = {
                    'cpu_usage': None,
                    'memory_usage': None,
                    'disk_io': None
                }
            else:
                result = results[0]
                
                # Convert percentages to decimals (75.5% -> 0.755)
                cpu_pct = self._safe_float(result.get('cpu.usage'))
                cpu_usage = (cpu_pct / 100.0) if cpu_pct is not None else None
                
                memory_pct = self._safe_float(result.get('memory.usage'))
                memory_usage = (memory_pct / 100.0) if memory_pct is not None else None
                
                # disk_io already in MB/s from NRQL calculation
                disk_io = self._safe_float(result.get('disk.io'))
                
                metrics = {
                    'cpu_usage': cpu_usage,
                    'memory_usage': memory_usage,
                    'disk_io': disk_io
                }
            
            # Generate current timestamp with UTC indicator
            timestamp = datetime.utcnow().isoformat() + 'Z'
            
            # Build response dictionary
            response_dict = {
                'app_id': app_id,
                'timestamp': timestamp,
                'infrastructure': metrics
            }
            
            # Log success
            self._logger.info(
                f"[INFO] [api_client] Fetched infrastructure metrics for app_id={app_id}, days={days}"
            )
            
            return response_dict
            
        except Exception as e:
            # Log error with context
            error_msg = f"Failed to fetch infrastructure metrics: {type(e).__name__}: {str(e)}"
            self._logger.error(
                f"[ERROR] [api_client] {error_msg}. app_id={app_id}, days={days}"
            )
            # Re-raise original exception
            raise
    
    def fetch_database_metrics(
        self, 
        app_id: str, 
        days: int
    ) -> Dict[str, Any]:
        """
        Fetch database metrics for a specific application.
        
        Retrieves query time, slow queries, connection pool usage, and database calls
        for the specified time window.
        
        Args:
            app_id: New Relic application ID
            days: Time window in days (must be 3, 7, 14, or 30)
            
        Returns:
            Dictionary with structure:
            {
                "app_id": str,
                "timestamp": str (ISO 8601),
                "database": {
                    "query_time": float or None (milliseconds),
                    "slow_queries": int or None,
                    "connection_pool_usage": float or None (0.0 to 1.0),
                    "database_calls": int or None
                }
            }
            
        Raises:
            ValueError: If app_id is empty or days not in [3, 7, 14, 30]
            requests.exceptions.*: For API request failures
        """
        from datetime import datetime, timedelta
        
        # Validate app_id
        if not app_id or not app_id.strip():
            raise ValueError("app_id cannot be empty")
        
        # Validate days parameter
        ALLOWED_DAYS = [3, 7, 14, 30]
        if days not in ALLOWED_DAYS:
            raise ValueError(f"days must be one of {ALLOWED_DAYS}, got {days}")
        
        # Calculate time window (since timestamp)
        since = datetime.utcnow() - timedelta(days=days)
        since_iso = since.isoformat() + 'Z'  # Add 'Z' for UTC
        
        # Construct NerdGraph NRQL query for database metrics
        # Note: NRQL string must have values injected via f-string, not GraphQL variables
        nrql_query = f"SELECT average(databaseDuration) * 1000 as 'query.time', count(*) FILTER(WHERE databaseDuration > 1.0) as 'slow.queries', average(databaseCallCount) as 'db.calls', percentage(count(*), WHERE databaseCallCount > 10) as 'pool.usage' FROM Transaction WHERE appId = '{app_id}' SINCE '{since_iso}'"
        
        query = f"""
        query($accountId: Int!) {{
          actor {{
            account(id: $accountId) {{
              nrql(query: "{nrql_query}") {{
                results
              }}
            }}
          }}
        }}
        """
        
        variables = {
            'accountId': int(self._account_id)
        }
        
        try:
            # Make API request
            self._logger.debug(
                f"[DEBUG] [api_client] Fetching database metrics: "
                f"app_id={app_id}, days={days}, since={since_iso}"
            )
            
            response = self._make_request(query, variables)
            
            # Extract metrics from response
            results = response.get('data', {}).get('actor', {}).get('account', {}).get('nrql', {}).get('results', [])
            
            if not results:
                # No data available
                metrics = {
                    'query_time': None,
                    'slow_queries': None,
                    'connection_pool_usage': None,
                    'database_calls': None
                }
            else:
                result = results[0]
                
                # query_time already in milliseconds from NRQL (* 1000)
                query_time = self._safe_float(result.get('query.time'))
                
                # slow_queries as integer
                slow_queries = self._safe_int(result.get('slow.queries'))
                
                # database_calls as integer
                database_calls = self._safe_int(result.get('db.calls'))
                
                # Convert pool usage from percentage to decimal
                pool_pct = self._safe_float(result.get('pool.usage'))
                connection_pool_usage = (pool_pct / 100.0) if pool_pct is not None else None
                
                metrics = {
                    'query_time': query_time,
                    'slow_queries': slow_queries,
                    'connection_pool_usage': connection_pool_usage,
                    'database_calls': database_calls
                }
            
            # Generate current timestamp with UTC indicator
            timestamp = datetime.utcnow().isoformat() + 'Z'
            
            # Build response dictionary
            response_dict = {
                'app_id': app_id,
                'timestamp': timestamp,
                'database': metrics
            }
            
            # Log success
            self._logger.info(
                f"[INFO] [api_client] Fetched database metrics for app_id={app_id}, days={days}"
            )
            
            return response_dict
            
        except Exception as e:
            # Log error with context
            error_msg = f"Failed to fetch database metrics: {type(e).__name__}: {str(e)}"
            self._logger.error(
                f"[ERROR] [api_client] {error_msg}. app_id={app_id}, days={days}"
            )
            # Re-raise original exception
            raise
    
    def fetch_transaction_metrics(
        self, 
        app_id: str, 
        days: int
    ) -> Dict[str, Any]:
        """
        Fetch transaction/API metrics for a specific application.
        
        Retrieves transaction time, external calls, and API endpoint performance
        for the specified time window.
        
        Args:
            app_id: New Relic application ID
            days: Time window in days (must be 3, 7, 14, or 30)
            
        Returns:
            Dictionary with structure:
            {
                "app_id": str,
                "timestamp": str (ISO 8601),
                "transactions": {
                    "transaction_time": float or None (milliseconds),
                    "external_calls": int or None,
                    "external_latency": float or None (milliseconds),
                    "api_endpoints": list or None (top endpoints with performance)
                }
            }
            
        Raises:
            ValueError: If app_id is empty or days not in [3, 7, 14, 30]
            requests.exceptions.*: For API request failures
        """
        from datetime import datetime, timedelta
        
        # Validate app_id
        if not app_id or not app_id.strip():
            raise ValueError("app_id cannot be empty")
        
        # Validate days parameter
        ALLOWED_DAYS = [3, 7, 14, 30]
        if days not in ALLOWED_DAYS:
            raise ValueError(f"days must be one of {ALLOWED_DAYS}, got {days}")
        
        # Calculate time window (since timestamp)
        since = datetime.utcnow() - timedelta(days=days)
        since_iso = since.isoformat() + 'Z'  # Add 'Z' for UTC
        
        # Construct NerdGraph NRQL query for transaction metrics
        # Note: NRQL string must have values injected via f-string, not GraphQL variables
        nrql_query = f"SELECT average(duration) * 1000 as 'transaction.time', count(*) FILTER(WHERE externalDuration > 0) as 'external.calls', average(externalDuration) * 1000 as 'external.latency', uniques(name) as 'api.endpoints' FROM Transaction WHERE appId = '{app_id}' SINCE '{since_iso}'"
        
        query = f"""
        query($accountId: Int!) {{
          actor {{
            account(id: $accountId) {{
              nrql(query: "{nrql_query}") {{
                results
              }}
            }}
          }}
        }}
        """
        
        variables = {
            'accountId': int(self._account_id)
        }
        
        try:
            # Make API request
            self._logger.debug(
                f"[DEBUG] [api_client] Fetching transaction metrics: "
                f"app_id={app_id}, days={days}, since={since_iso}"
            )
            
            response = self._make_request(query, variables)
            
            # Extract metrics from response
            results = response.get('data', {}).get('actor', {}).get('account', {}).get('nrql', {}).get('results', [])
            
            if not results:
                # No data available
                metrics = {
                    'transaction_time': None,
                    'external_calls': None,
                    'external_latency': None,
                    'api_endpoints': None
                }
            else:
                result = results[0]
                
                # Transaction time in milliseconds (already converted in NRQL)
                transaction_time = self._safe_float(result.get('transaction.time'))
                
                # External calls count
                external_calls = self._safe_int(result.get('external.calls'))
                
                # External latency in milliseconds (already converted in NRQL)
                external_latency = self._safe_float(result.get('external.latency'))
                
                # Parse API endpoints (may be array or comma-separated string)
                api_endpoints_raw = result.get('api.endpoints')
                if api_endpoints_raw is None:
                    api_endpoints = None
                elif isinstance(api_endpoints_raw, list):
                    api_endpoints = [str(e) for e in api_endpoints_raw if e]
                elif isinstance(api_endpoints_raw, str):
                    # Handle comma-separated string
                    api_endpoints = [e.strip() for e in api_endpoints_raw.split(',') if e.strip()]
                else:
                    api_endpoints = None
                
                metrics = {
                    'transaction_time': transaction_time,
                    'external_calls': external_calls,
                    'external_latency': external_latency,
                    'api_endpoints': api_endpoints
                }
            
            # Generate current timestamp with UTC indicator
            timestamp = datetime.utcnow().isoformat() + 'Z'
            
            # Build response dictionary
            response_dict = {
                'app_id': app_id,
                'timestamp': timestamp,
                'transactions': metrics
            }
            
            # Log success
            self._logger.info(
                f"[INFO] [api_client] Fetched transaction metrics for app_id={app_id}, days={days}"
            )
            
            return response_dict
            
        except Exception as e:
            # Log error with context
            error_msg = f"Failed to fetch transaction metrics: {type(e).__name__}: {str(e)}"
            self._logger.error(
                f"[ERROR] [api_client] {error_msg}. app_id={app_id}, days={days}"
            )
            # Re-raise original exception
            raise
    
    def collect_all_metrics(
        self,
        app_id: str,
        days: int,
        app_name: str = "app",
        use_cache: bool = True,
        cache_ttl: int = 3600
    ) -> Dict[str, Any]:
        """
        Collect all metric categories with caching and progress indicators.
        
        Args:
            app_id: New Relic application ID
            days: Time window in days (must be 3, 7, 14, or 30)
            app_name: Application name for cache file naming
            use_cache: Whether to use cached data if available
            cache_ttl: Cache time-to-live in seconds (default: 3600)
            
        Returns:
            Dictionary with all metric categories
        """
        # Validate inputs early (fail-fast)
        if not app_id or not app_id.strip():
            raise ValueError("app_id cannot be empty")
        
        ALLOWED_DAYS = [3, 7, 14, 30]
        if days not in ALLOWED_DAYS:
            raise ValueError(f"days must be one of {ALLOWED_DAYS}, got {days}")
        
        # Check for cached data
        if use_cache:
            cached_data = self.load_from_cache(app_name, cache_ttl)
            if cached_data:
                return cached_data
        
        # Collect all metrics with progress indicators
        print(f"Collecting metrics for {app_name}...")
        
        all_metrics = {
            'app_id': app_id,
            'app_name': app_name,
            'collection_timestamp': datetime.utcnow().isoformat() + 'Z',
            'time_window_days': days
        }
        
        # Story 2.2: Performance metrics
        print("Fetching performance metrics... (1/5)")
        start_time = time.time()
        all_metrics['performance'] = self.fetch_performance_metrics(app_id, days)
        duration_ms = int((time.time() - start_time) * 1000)
        self._logger.info(f"[INFO] [api_client] Performance metrics collected in {duration_ms}ms")
        
        # Story 2.3: Error metrics
        print("Fetching error metrics... (2/5)")
        start_time = time.time()
        all_metrics['errors'] = self.fetch_error_metrics(app_id, days)
        duration_ms = int((time.time() - start_time) * 1000)
        self._logger.info(f"[INFO] [api_client] Error metrics collected in {duration_ms}ms")
        
        # Story 2.4: Infrastructure metrics
        print("Fetching infrastructure metrics... (3/5)")
        start_time = time.time()
        all_metrics['infrastructure'] = self.fetch_infrastructure_metrics(app_id, days)
        duration_ms = int((time.time() - start_time) * 1000)
        self._logger.info(f"[INFO] [api_client] Infrastructure metrics collected in {duration_ms}ms")
        
        # Story 2.5: Database metrics
        print("Fetching database metrics... (4/5)")
        start_time = time.time()
        all_metrics['database'] = self.fetch_database_metrics(app_id, days)
        duration_ms = int((time.time() - start_time) * 1000)
        self._logger.info(f"[INFO] [api_client] Database metrics collected in {duration_ms}ms")
        
        # Story 2.6: Transaction metrics
        print("Fetching transaction metrics... (5/5)")
        start_time = time.time()
        all_metrics['transactions'] = self.fetch_transaction_metrics(app_id, days)
        duration_ms = int((time.time() - start_time) * 1000)
        self._logger.info(f"[INFO] [api_client] Transaction metrics collected in {duration_ms}ms")
        
        print("✓ Data collection complete")
        
        # Save to cache
        if use_cache:
            cache_file = self.save_to_cache(all_metrics, app_name)
            print(f"Data saved to: {cache_file}")
        
        return all_metrics
    
    def save_to_cache(self, data: Dict[str, Any], app_name: str) -> str:
        """
        Save collected metrics to cache file.
        
        Args:
            data: Metrics dictionary to cache
            app_name: Application name for file naming
            
        Returns:
            Path to saved cache file
        """
        # Create data directory if it doesn't exist
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp_str = datetime.utcnow().strftime("%Y-%m-%d-%H%M%S")
        filename = f"{app_name}-{timestamp_str}.json"
        filepath = os.path.join(data_dir, filename)
        
        # Write JSON with indentation
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        self._logger.info(f"[INFO] [api_client] Saved metrics to cache: {filepath}")
        
        return filepath
    
    def load_from_cache(self, app_name: str, cache_ttl: int = 3600) -> Optional[Dict[str, Any]]:
        """
        Load cached metrics if available and fresh.
        
        Args:
            app_name: Application name to find cache file
            cache_ttl: Cache time-to-live in seconds
            
        Returns:
            Cached data if fresh, None otherwise
        """
        data_dir = "data"
        if not os.path.exists(data_dir):
            return None
        
        # Find most recent cache file for this app (by modification time)
        pattern = os.path.join(data_dir, f"{app_name}-*.json")
        cache_files = glob.glob(pattern)
        
        if not cache_files:
            return None
        
        # Get newest file by modification time
        latest_cache = max(cache_files, key=os.path.getmtime)
        
        # Check file age
        file_mtime = os.path.getmtime(latest_cache)
        age_seconds = time.time() - file_mtime
        
        if age_seconds > cache_ttl:
            age_minutes = int(age_seconds / 60)
            self._logger.info(f"[INFO] [api_client] Cache stale (age: {age_minutes} minutes), fetching fresh data")
            return None
        
        # Load and return cached data
        try:
            with open(latest_cache, 'r') as f:
                data = json.load(f)
            
            age_minutes = int(age_seconds / 60)
            self._logger.info(f"[INFO] [api_client] Using cached data from {latest_cache}")
            print(f"Using cached data (age: {age_minutes} minutes)")
            
            return data
        except Exception as e:
            self._logger.error(f"[ERROR] [api_client] Failed to load cache: {e}")
            return None
    
    def cleanup_old_cache(self, retention_days: int = 30) -> int:
        """
        Remove cache files older than retention period.
        
        Args:
            retention_days: Number of days to retain cache files
            
        Returns:
            Number of files deleted
        """
        data_dir = "data"
        if not os.path.exists(data_dir):
            return 0
        
        # Find all JSON files
        pattern = os.path.join(data_dir, "*.json")
        cache_files = glob.glob(pattern)
        
        retention_seconds = retention_days * 24 * 60 * 60
        current_time = time.time()
        deleted_count = 0
        
        for filepath in cache_files:
            file_age = current_time - os.path.getmtime(filepath)
            
            if file_age > retention_seconds:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                    self._logger.debug(f"[DEBUG] [api_client] Deleted old cache file: {filepath}")
                except Exception as e:
                    self._logger.error(f"[ERROR] [api_client] Failed to delete {filepath}: {e}")
        
        if deleted_count > 0:
            self._logger.info(f"[INFO] [api_client] Cleaned up {deleted_count} old cache files")
        
        return deleted_count
