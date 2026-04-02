"""
CA certificates utilities.

Load CA certificates for TLS connections.
"""

import os
import ssl
import logging
from functools import lru_cache
from typing import List, Optional

logger = logging.getLogger(__name__)

# Cache for CA certificates
_certs_cache: Optional[List[str]] = None


# Placeholder for has_node_option
def _has_node_option(flag: str) -> bool:
    """Check if NODE_OPTIONS contains a specific flag."""
    node_options = os.environ.get("NODE_OPTIONS")
    if not node_options:
        return False
    return flag in node_options.split()


# Placeholder for get_fs_implementation
def _get_fs_implementation() -> Any:
    """Get filesystem implementation placeholder."""
    class FSImpl:
        def read_file_sync(self, path: str, encoding: str = "utf-8") -> str:
            with open(path, "r", encoding=encoding if encoding == "utf-8" else None) as f:
                return f.read()
    return FSImpl()


@lru_cache(maxsize=1)
def get_ca_certificates() -> Optional[List[str]]:
    """Load CA certificates for TLS connections.

    Since setting `ca` on an HTTPS agent replaces the default certificate store,
    we must always include base CAs when returning.

    Returns:
        List of CA certificates, or None if no custom CA configuration is needed
    """
    global _certs_cache
    if _certs_cache is not None:
        return _certs_cache

    use_system_ca = _has_node_option("--use-system-ca") or _has_node_option("--use-openssl-ca")
    extra_certs_path = os.environ.get("NODE_EXTRA_CA_CERTS")

    logger.debug(f"CA certs: useSystemCA={use_system_ca}, extraCertsPath={extra_certs_path}")

    # If neither is set, return None (use runtime defaults)
    if not use_system_ca and not extra_certs_path:
        return None

    certs: List[str] = []

    if use_system_ca:
        # Try to get system CA store
        try:
            # Python's SSL module doesn't expose system CAs directly
            # Use certifi if available, otherwise return None
            try:
                import certifi
                system_ca_path = certifi.where()
                with open(system_ca_path, "r") as f:
                    certs.append(f.read())
                logger.debug(f"CA certs: Loaded system CA certificates from certifi")
            except ImportError:
                logger.debug("CA certs: certifi not available, cannot load system CAs")
                if not extra_certs_path:
                    return None
        except Exception as e:
            logger.debug(f"CA certs: Failed to load system CAs: {e}")
    else:
        # Include bundled Mozilla CAs as base
        try:
            import certifi
            bundled_ca_path = certifi.where()
            with open(bundled_ca_path, "r") as f:
                certs.append(f.read())
            logger.debug(f"CA certs: Loaded {len(certs)} bundled root certificates as base")
        except ImportError:
            logger.debug("CA certs: certifi not available")

    # Append extra certs from file
    if extra_certs_path:
        try:
            fs = _get_fs_implementation()
            extra_cert = fs.read_file_sync(extra_certs_path, "utf-8")
            certs.append(extra_cert)
            logger.debug(f"CA certs: Appended extra certificates from NODE_EXTRA_CA_CERTS ({extra_certs_path})")
        except Exception as error:
            logger.debug(f"CA certs: Failed to read NODE_EXTRA_CA_CERTS file ({extra_certs_path}): {error}")

    _certs_cache = certs if certs else None
    return _certs_cache


def clear_ca_certs_cache() -> None:
    """Clear the CA certificates cache.

    Call this when environment variables that affect CA certs may have changed.
    """
    global _certs_cache
    _certs_cache = None
    get_ca_certificates.cache_clear()
    logger.debug("Cleared CA certificates cache")


__all__ = ["get_ca_certificates", "clear_ca_certs_cache"]