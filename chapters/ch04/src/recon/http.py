"""
Listing 4.4: HTTPS Probing

Provides functions for sending safe HTTPS HEAD requests
to collect response headers with minimal traffic footprint.
"""

import http.client
import ssl
from typing import Dict, List, Tuple

from src.recon.constants import DEFAULT_TIMEOUT, DEFAULT_USER_AGENT


def https_head(
    host: str,
    timeout: int = DEFAULT_TIMEOUT,
    user_agent: str = DEFAULT_USER_AGENT,
    path: str = "/",
) -> Tuple[Dict[str, str], List[str]]:
    """
    Send a safe HTTPS HEAD request and return headers with notes.

    Uses HEAD instead of GET because we only need response headers.
    This keeps our traffic footprint minimal.

    Args:
        host: Target hostname
        timeout: Connection timeout in seconds
        user_agent: User-Agent header value
        path: URL path to request (default: "/")

    Returns:
        Tuple of (headers, notes)
        - headers: Dictionary of lowercase header names to values
        - notes: List of observations (status code, errors)

    Example:
        >>> headers, notes = https_head("example.com")
        >>> print(notes)
        ['status:200']
        >>> print(headers.get('server'))
        'ECS (nyb/1D2D)'
    """
    headers: Dict[str, str] = {}
    notes: List[str] = []
    conn = None

    try:
        ctx = ssl.create_default_context()
        conn = http.client.HTTPSConnection(host, 443, context=ctx, timeout=timeout)
        conn.request("HEAD", path, headers={"User-Agent": user_agent})
        res = conn.getresponse()

        # Normalize header names to lowercase for consistent access
        headers = {k.lower(): v for k, v in res.getheaders()}
        notes.append(f"status:{res.status}")

    except ssl.SSLError as e:
        notes.append(f"error:SSLError:{e.reason if hasattr(e, 'reason') else str(e)}")
    except http.client.HTTPException as e:
        notes.append(f"error:{type(e).__name__}")
    except (ConnectionError, TimeoutError) as e:
        notes.append(f"error:{type(e).__name__}")
    except OSError as e:
        notes.append(f"error:OSError:{e.errno}")
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

    return headers, notes


def http_head(
    host: str,
    timeout: int = DEFAULT_TIMEOUT,
    user_agent: str = DEFAULT_USER_AGENT,
    path: str = "/",
) -> Tuple[Dict[str, str], List[str]]:
    """
    Send a plain HTTP HEAD request (no TLS).

    Useful for hosts that don't support HTTPS or as a fallback.

    Args:
        host: Target hostname
        timeout: Connection timeout in seconds
        user_agent: User-Agent header value
        path: URL path to request

    Returns:
        Tuple of (headers, notes)
    """
    headers: Dict[str, str] = {}
    notes: List[str] = []
    conn = None

    try:
        conn = http.client.HTTPConnection(host, 80, timeout=timeout)
        conn.request("HEAD", path, headers={"User-Agent": user_agent})
        res = conn.getresponse()

        headers = {k.lower(): v for k, v in res.getheaders()}
        notes.append(f"status:{res.status}")
        notes.append("protocol:http")

    except http.client.HTTPException as e:
        notes.append(f"error:{type(e).__name__}")
    except (ConnectionError, TimeoutError) as e:
        notes.append(f"error:{type(e).__name__}")
    except OSError as e:
        notes.append(f"error:OSError:{e.errno}")
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

    return headers, notes
