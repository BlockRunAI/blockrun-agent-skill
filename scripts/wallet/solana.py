"""
BlockRun Solana Wallet Module - Solana wallet balance and status queries.

Query USDC-SPL balance on Solana for BlockRun payments.
"""

from typing import Optional


try:
    from blockrun_llm import get_or_create_solana_wallet, get_solana_usdc_balance
    HAS_SOLANA = True
except ImportError:
    HAS_SOLANA = False


def get_solana_wallet_address(private_key: Optional[str] = None) -> str:
    """
    Get the Solana wallet address.

    Args:
        private_key: Override with specific bs58 private key

    Returns:
        Solana wallet address (base58)
    """
    if not HAS_SOLANA:
        raise ImportError(
            "blockrun_llm[solana] not installed. "
            "Install with: pip install blockrun-llm[solana]"
        )

    if private_key:
        from blockrun_llm import get_solana_public_key
        return get_solana_public_key(private_key)

    result = get_or_create_solana_wallet()
    return result["address"]


def get_solana_balance(private_key: Optional[str] = None) -> dict:
    """
    Get Solana wallet balance information.

    Args:
        private_key: Override with specific bs58 private key

    Returns:
        Dict with wallet info:
        {
            "address": "7AKU...",
            "network": "Solana (Mainnet)",
            "balance": 0.0,
            "balance_url": "https://solscan.io/account/..."
        }
    """
    address = get_solana_wallet_address(private_key)
    balance = get_solana_usdc_balance(address)

    return {
        "address": address,
        "network": "Solana (Mainnet)",
        "balance": balance,
        "balance_url": f"https://solscan.io/account/{address}",
    }


def get_solana_wallet_status(private_key: Optional[str] = None) -> dict:
    """
    Get comprehensive Solana wallet status.

    Args:
        private_key: Override with specific bs58 private key

    Returns:
        Dict with wallet status information
    """
    try:
        address = get_solana_wallet_address(private_key)
        return {
            "status": "connected",
            "address": address,
            "network": "Solana (Mainnet)",
            "currency": "USDC",
            "explorer_url": f"https://solscan.io/account/{address}",
        }
    except ImportError as e:
        return {
            "status": "not_installed",
            "error": str(e),
            "help": "pip install blockrun-llm[solana]",
        }
    except ValueError as e:
        return {
            "status": "not_configured",
            "error": str(e),
            "help": "Set SOLANA_WALLET_KEY environment variable or run setup_agent_solana_wallet()",
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }
