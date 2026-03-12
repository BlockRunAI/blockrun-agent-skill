"""
BlockRun Configuration Module.

Handles configuration management, environment variables, and presets.
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path


# Wallet storage location (agent's own wallet)
WALLET_DIR = Path.home() / ".blockrun"
WALLET_FILE = WALLET_DIR / ".session"
SOLANA_WALLET_FILE = WALLET_DIR / ".solana-session"


# Default configuration values
DEFAULTS = {
    "api_url": "https://blockrun.ai/api",
    "default_model": "openai/gpt-5.2",
    "default_image_model": "google/nano-banana",
    "max_tokens": 1024,
    "timeout": 60.0,
    "image_timeout": 120.0,
}


def load_wallet() -> Optional[str]:
    """
    Load wallet private key from ~/.blockrun/.session file.

    AI agents should have their own wallets. This is the agent's wallet.

    Returns:
        Private key string or None if not found
    """
    # Check .session first (preferred)
    if WALLET_FILE.exists():
        key = WALLET_FILE.read_text().strip()
        if key:
            return key

    # Check legacy wallet.key
    legacy_file = WALLET_DIR / "wallet.key"
    if legacy_file.exists():
        key = legacy_file.read_text().strip()
        if key:
            return key

    return None


def get_private_key() -> Optional[str]:
    """
    Get private key - session file first (agent wallet), then env vars (user override).

    Priority:
        1. ~/.blockrun/.session - Agent's own wallet
        2. BLOCKRUN_WALLET_KEY env var - User override
        3. BASE_CHAIN_WALLET_KEY env var - Legacy fallback

    Returns:
        Private key string or None
    """
    # PRIORITY 1: Agent's own wallet (session file)
    session_key = load_wallet()
    if session_key:
        return session_key

    # PRIORITY 2: User override via environment
    return (
        os.environ.get("BLOCKRUN_WALLET_KEY") or
        os.environ.get("BASE_CHAIN_WALLET_KEY")
    )


def load_solana_wallet() -> Optional[str]:
    """
    Load Solana wallet private key from ~/.blockrun/.solana-session file.

    Returns:
        bs58-encoded private key string or None if not found
    """
    if SOLANA_WALLET_FILE.exists():
        key = SOLANA_WALLET_FILE.read_text().strip()
        if key:
            return key
    return None


def get_solana_private_key() -> Optional[str]:
    """
    Get Solana private key - env var first, then session file.

    Priority:
        1. SOLANA_WALLET_KEY env var
        2. ~/.blockrun/.solana-session file

    Returns:
        bs58-encoded private key string or None
    """
    env_key = os.environ.get("SOLANA_WALLET_KEY")
    if env_key:
        return env_key
    return load_solana_wallet()


def get_config() -> Dict[str, Any]:
    """
    Get current configuration from environment and defaults.

    Returns:
        Configuration dictionary
    """
    return {
        "api_url": os.environ.get("BLOCKRUN_API_URL", DEFAULTS["api_url"]),
        "wallet_key_set": bool(get_private_key()),
        "default_model": os.environ.get("BLOCKRUN_DEFAULT_MODEL", DEFAULTS["default_model"]),
        "default_image_model": os.environ.get("BLOCKRUN_IMAGE_MODEL", DEFAULTS["default_image_model"]),
        "max_tokens": int(os.environ.get("BLOCKRUN_MAX_TOKENS", DEFAULTS["max_tokens"])),
        "timeout": float(os.environ.get("BLOCKRUN_TIMEOUT", DEFAULTS["timeout"])),
    }


def validate_config() -> Dict[str, Any]:
    """
    Validate configuration and return status.

    Returns:
        Dict with validation results:
        {
            "valid": bool,
            "errors": list of error strings,
            "warnings": list of warning strings,
        }
    """
    errors = []
    warnings = []

    # Check for wallet key
    if not get_private_key():
        errors.append("No wallet found (check ~/.blockrun/.session or BLOCKRUN_WALLET_KEY)")

    # Check API URL format
    api_url = os.environ.get("BLOCKRUN_API_URL", DEFAULTS["api_url"])
    if not api_url.startswith(("http://", "https://")):
        errors.append("Invalid BLOCKRUN_API_URL format")

    # Warnings for non-default settings
    if os.environ.get("BLOCKRUN_API_URL"):
        warnings.append("Using custom API URL (not default)")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def get_presets_dir() -> Path:
    """Get path to presets directory."""
    return Path(__file__).parent.parent.parent / "configs" / "presets"


def list_presets() -> list:
    """
    List available configuration presets.

    Returns:
        List of preset names
    """
    presets_dir = get_presets_dir()
    if not presets_dir.exists():
        return []

    return [
        f.stem for f in presets_dir.glob("*.json")
    ]
