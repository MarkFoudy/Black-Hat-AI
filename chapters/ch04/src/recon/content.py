"""
Listing 4.7: Content Inspection

Provides functions to retrieve and parse robots.txt and sitemap
information from target hosts.
"""

import http.client
import ssl
from typing import List, Tuple

from src.recon.constants import DEFAULT_TIMEOUT, DEFAULT_USER_AGENT, MAX_ROBOTS_SIZE


def robots_and_sitemap(
    host: str,
    timeout: int = DEFAULT_TIMEOUT,
    user_agent: str = DEFAULT_USER_AGENT,
) -> List[str]:
    """
    Retrieve /robots.txt to note presence and capture sitemap hints.

    Sitemaps are goldmines: they enumerate URLs the site wants indexed,
    which produces paths we'd otherwise have to guess.

    Args:
        host: Target hostname
        timeout: Connection timeout in seconds
        user_agent: User-Agent header value

    Returns:
        List of notes including:
        - robots:yes/no/error
        - sitemap:<url> for each sitemap directive found

    Note:
        This function is gated behind --content flag in the CLI
        to keep the default run ultra-lightweight.

    Example:
        >>> notes = robots_and_sitemap("example.com")
        >>> print(notes)
        ['robots:yes', 'sitemap:https://example.com/sitemap.xml']
    """
    notes: List[str] = []
    conn = None

    try:
        ctx = ssl.create_default_context()
        conn = http.client.HTTPSConnection(host, 443, context=ctx, timeout=timeout)
        conn.request("GET", "/robots.txt", headers={"User-Agent": user_agent})
        res = conn.getresponse()

        robots_ok = 200 <= res.status < 400
        notes.append("robots:yes" if robots_ok else "robots:no")

        if robots_ok:
            # Read with size limit to prevent downloading huge files
            body = res.read(MAX_ROBOTS_SIZE).decode("utf-8", errors="ignore")
            for line in body.splitlines():
                line_lower = line.lower().strip()
                if line_lower.startswith("sitemap:"):
                    sitemap_url = line.split(":", 1)[1].strip()
                    notes.append(f"sitemap:{sitemap_url}")

    except ssl.SSLError:
        notes.append("robots:error:ssl")
    except http.client.HTTPException:
        notes.append("robots:error:http")
    except (ConnectionError, TimeoutError):
        notes.append("robots:error:connection")
    except OSError:
        notes.append("robots:error:os")
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

    return notes


def parse_robots_txt(content: str) -> dict:
    """
    Parse robots.txt content into structured data.

    Args:
        content: Raw robots.txt content

    Returns:
        Dictionary with:
        - user_agents: Dict mapping user-agent to rules
        - sitemaps: List of sitemap URLs
        - crawl_delay: Crawl delay if specified
    """
    result = {
        "user_agents": {},
        "sitemaps": [],
        "crawl_delay": None,
    }

    current_ua = "*"

    for line in content.splitlines():
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        # Parse directive
        if ":" not in line:
            continue

        directive, value = line.split(":", 1)
        directive = directive.strip().lower()
        value = value.strip()

        if directive == "user-agent":
            current_ua = value
            if current_ua not in result["user_agents"]:
                result["user_agents"][current_ua] = {"allow": [], "disallow": []}

        elif directive == "disallow":
            if current_ua not in result["user_agents"]:
                result["user_agents"][current_ua] = {"allow": [], "disallow": []}
            result["user_agents"][current_ua]["disallow"].append(value)

        elif directive == "allow":
            if current_ua not in result["user_agents"]:
                result["user_agents"][current_ua] = {"allow": [], "disallow": []}
            result["user_agents"][current_ua]["allow"].append(value)

        elif directive == "sitemap":
            result["sitemaps"].append(value)

        elif directive == "crawl-delay":
            try:
                result["crawl_delay"] = float(value)
            except ValueError:
                pass

    return result


def fetch_robots_txt(
    host: str,
    timeout: int = DEFAULT_TIMEOUT,
    user_agent: str = DEFAULT_USER_AGENT,
) -> Tuple[str, int]:
    """
    Fetch raw robots.txt content.

    Args:
        host: Target hostname
        timeout: Connection timeout in seconds
        user_agent: User-Agent header value

    Returns:
        Tuple of (content, status_code)
        - content: Raw robots.txt text or empty string on error
        - status_code: HTTP status code or -1 on error
    """
    conn = None

    try:
        ctx = ssl.create_default_context()
        conn = http.client.HTTPSConnection(host, 443, context=ctx, timeout=timeout)
        conn.request("GET", "/robots.txt", headers={"User-Agent": user_agent})
        res = conn.getresponse()

        if 200 <= res.status < 400:
            body = res.read(MAX_ROBOTS_SIZE).decode("utf-8", errors="ignore")
            return body, res.status
        else:
            return "", res.status

    except Exception:
        return "", -1
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
