#!/usr/bin/env python3
"""
BlockRun Claude Code Wallet - Unified CLI Entry Point

Access unlimited LLM models and image generation through USDC micropayments.
Your private key never leaves your machine - only signatures are transmitted.

Usage:
    python run.py "Your prompt here"
    python run.py "Prompt" --model openai/gpt-5.2
    python run.py "Description" --image
    python run.py --balance
    python run.py --models

Environment:
    BLOCKRUN_WALLET_KEY: Your Base chain wallet private key (required)
    BLOCKRUN_API_URL: API endpoint (optional, default: https://blockrun.ai/api)
"""

import argparse
import base64
import json
import os
import re
import sys
import urllib.request
import urllib.error
from typing import Optional

# Plugin version (keep in sync with plugin.json)
__version__ = "1.0.0"
GITHUB_PLUGIN_URL = "https://raw.githubusercontent.com/BlockRunAI/blockrun-agent-wallet/main/plugin.json"

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from scripts.utils.branding import branding
    from scripts.utils.spending import SpendingTracker
except ImportError:
    # Fallback if running directly
    from utils.branding import branding
    from utils.spending import SpendingTracker

# Try to import blockrun_llm SDK
try:
    from blockrun_llm import LLMClient, ImageClient, APIError, PaymentError
    HAS_SDK = True
except ImportError:
    HAS_SDK = False


def check_environment() -> bool:
    """Check if wallet is available (session file or env var)."""
    try:
        from scripts.utils.config import get_private_key
    except ImportError:
        from utils.config import get_private_key

    key = get_private_key()
    if not key:
        branding.print_error(
            "No wallet found",
            help_link="https://blockrun.ai/docs/setup"
        )
        print("  Wallet auto-creates on first use, or set manually:")
        print("    export BLOCKRUN_WALLET_KEY=\"0x...\"")
        print()
        return False
    return True


def is_realtime_query(prompt: str) -> bool:
    """Check if prompt requires real-time data (Twitter/X)."""
    prompt_lower = prompt.lower()

    # Direct keywords for real-time/social media queries
    keywords = [
        "twitter", "x.com", "trending", "elon", "musk",
        "breaking news", "latest posts", "live updates",
        "what are people saying", "current events"
    ]
    if any(word in prompt_lower for word in keywords):
        return True

    # Twitter handle pattern (@username but not email)
    # Match @ followed by word chars, not preceded by word char (excludes email)
    if re.search(r'(?<!\w)@\w+', prompt_lower):
        return True

    return False


def get_smart_model(prompt: str, cheap: bool = False, fast: bool = False) -> str:
    """
    Smart model routing based on prompt content and preferences.

    Args:
        prompt: User's prompt text
        cheap: Prefer cost-effective models
        fast: Prefer low-latency models

    Returns:
        Model ID string
    """
    prompt_lower = prompt.lower()

    # PRIORITY 1: Real-time data requires Grok (even with --cheap)
    # Grok is the only model with live X/Twitter access
    if is_realtime_query(prompt):
        return "xai/grok-3"

    # Warn if conflicting flags used
    if cheap and fast:
        branding.print_info("Note: --cheap and --fast both set; using --cheap")

    # Cost-optimized routing
    if cheap:
        return "deepseek/deepseek-chat"

    # Speed-optimized routing
    if fast:
        return "openai/gpt-5-mini"

    if any(word in prompt_lower for word in ["code", "python", "javascript", "function", "debug"]):
        return "anthropic/claude-sonnet-4"

    if any(word in prompt_lower for word in ["math", "proof", "prove", "theorem", "logic", "reasoning", "solve", "calculate"]):
        return "openai/o1-mini"

    if any(word in prompt_lower for word in ["long", "document", "summarize", "analyze file"]):
        return "google/gemini-2.0-flash"

    # Default: GPT-5.2 for general tasks
    return "openai/gpt-5.2"


def cmd_chat(
    prompt: str,
    model: Optional[str] = None,
    system: Optional[str] = None,
    cheap: bool = False,
    fast: bool = False,
    max_tokens: int = 1024,
    temperature: Optional[float] = None,
):
    """Execute chat command."""
    if not HAS_SDK:
        branding.print_error(
            "blockrun_llm SDK not installed",
            help_link="https://github.com/blockrunai/blockrun-llm"
        )
        print("  Install with: pip install blockrun-llm")
        return 1

    if not check_environment():
        return 1

    # Validate temperature if provided
    if temperature is not None and (temperature < 0.0 or temperature > 2.0):
        branding.print_error("Temperature must be between 0.0 and 2.0")
        return 1

    # Determine model
    selected_model = model or get_smart_model(prompt, cheap=cheap, fast=fast)

    # Check budget before making call
    tracker = SpendingTracker()
    within_budget, remaining = tracker.check_budget()
    if not within_budget:
        branding.print_budget_error(
            spent=tracker.get_total(),
            limit=tracker.get_limit(),
            calls=tracker.get_calls()
        )
        return 1

    try:
        client = LLMClient()

        # Print header
        branding.print_header(
            model=selected_model,
            wallet=client.get_wallet_address(),
        )

        # Auto-enable search for Grok real-time queries (Twitter/X)
        enable_search = is_realtime_query(prompt) and "grok" in selected_model.lower()

        # Execute chat
        response = client.chat(
            model=selected_model,
            prompt=prompt,
            system=system,
            max_tokens=max_tokens,
            temperature=temperature,
            search=enable_search,
        )

        # Print response
        branding.print_response(response)

        # Record spending
        sdk_spending = client.get_spending()
        call_cost = sdk_spending['total_usd']
        tracker.record(selected_model, call_cost)

        # Show spending with session totals
        budget_limit = tracker.get_limit()
        branding.print_footer(
            actual_cost=f"{call_cost:.4f}",
            session_total=tracker.get_total(),
            session_calls=tracker.get_calls(),
            budget_remaining=remaining - call_cost if budget_limit else None,
            budget_limit=budget_limit,
        )

        client.close()
        return 0

    except PaymentError as e:
        # Show funding instructions for insufficient balance
        wallet = None
        try:
            from blockrun_llm import get_wallet_address, open_wallet_qr
            wallet = get_wallet_address()
        except Exception:
            pass

        branding.print_error(f"Payment failed: {e}")
        if wallet:
            print(f"\n  Your wallet: {wallet}")
            print(f"  Network: Base (USDC)")
            print(f"\n  To fund your wallet:")
            print(f"    1. Send $1-5 USDC on Base to the address above")
            print(f"    2. Or run this to get a QR code:")
            print(f"       python -c \"from blockrun_llm import open_wallet_qr, get_wallet_address; open_wallet_qr(get_wallet_address())\"")
            print()
        return 1
    except APIError as e:
        error_str = str(e)
        if "400" in error_str:
            branding.print_error("Invalid request - model may not exist or parameters are wrong")
            print("\n  Run --models to see available models:")
            print("    python scripts/run.py --models\n")
        else:
            branding.print_error(f"API error: {e}")
        return 1
    except Exception as e:
        branding.print_error(f"Unexpected error: {e}")
        return 1


def cmd_image(
    prompt: str,
    model: Optional[str] = None,
    size: str = "1024x1024",
):
    """Execute image generation command."""
    if not HAS_SDK:
        branding.print_error(
            "blockrun_llm SDK not installed",
            help_link="https://github.com/blockrunai/blockrun-llm"
        )
        print("  Install with: pip install blockrun-llm")
        return 1

    if not check_environment():
        return 1

    selected_model = model or "google/nano-banana"

    # Check budget before making call
    tracker = SpendingTracker()
    within_budget, remaining = tracker.check_budget()
    if not within_budget:
        branding.print_budget_error(
            spent=tracker.get_total(),
            limit=tracker.get_limit(),
            calls=tracker.get_calls()
        )
        return 1

    try:
        client = ImageClient()

        # Print header
        branding.print_header(
            model=selected_model,
            wallet=client.get_wallet_address(),
        )

        branding.print_info(f"Generating image: \"{prompt[:50]}...\"")
        print()

        # Generate image
        result = client.generate(
            prompt=prompt,
            model=selected_model,
            size=size,
        )

        # Print result
        if result.data and len(result.data) > 0:
            image_url = result.data[0].url
            branding.print_success("Image generated!")

            # Save image to file
            import subprocess
            from datetime import datetime

            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"blockrun_image_{timestamp}.png"
            filepath = os.path.join(os.getcwd(), filename)

            try:
                # Handle base64 data URLs vs HTTP URLs
                if image_url.startswith('data:image/'):
                    # Extract and decode base64 data
                    # Format: data:image/png;base64,<data>
                    header, encoded_data = image_url.split(',', 1)
                    with open(filepath, 'wb') as f:
                        f.write(base64.b64decode(encoded_data))
                else:
                    # HTTP URL - download normally
                    urllib.request.urlretrieve(image_url, filepath)

                branding.print_success(f"Saved to: {filepath}")

                # Try to open with system viewer
                if sys.platform == "darwin":  # macOS
                    subprocess.run(["open", filepath], check=False)
                elif sys.platform == "linux":
                    subprocess.run(["xdg-open", filepath], check=False)
                elif sys.platform == "win32":
                    os.startfile(filepath)

            except Exception as e:
                # Don't dump the full URL (could be huge base64 string)
                url_preview = image_url[:80] + "..." if len(image_url) > 80 else image_url
                branding.print_error(f"Could not save image: {e}")
                print(f"  URL preview: {url_preview}\n")
        else:
            branding.print_error("No image data returned")

        # Record spending
        sdk_spending = client.get_spending()
        call_cost = sdk_spending['total_usd']
        tracker.record(selected_model, call_cost)

        # Show spending with session totals
        budget_limit = tracker.get_limit()
        branding.print_footer(
            actual_cost=f"{call_cost:.4f}",
            session_total=tracker.get_total(),
            session_calls=tracker.get_calls(),
            budget_remaining=remaining - call_cost if budget_limit else None,
            budget_limit=budget_limit,
        )

        client.close()
        return 0

    except PaymentError as e:
        # Show funding instructions for insufficient balance
        wallet = None
        try:
            from blockrun_llm import get_wallet_address
            wallet = get_wallet_address()
        except Exception:
            pass

        branding.print_error(f"Payment failed: {e}")
        if wallet:
            print(f"\n  Your wallet: {wallet}")
            print(f"  Network: Base (USDC)")
            print(f"\n  To fund your wallet:")
            print(f"    1. Send $1-5 USDC on Base to the address above")
            print(f"    2. Or run this to get a QR code:")
            print(f"       python -c \"from blockrun_llm import open_wallet_qr, get_wallet_address; open_wallet_qr(get_wallet_address())\"")
            print()
        return 1
    except APIError as e:
        error_str = str(e)
        if "400" in error_str:
            branding.print_error("Invalid request - check model and size parameters")
            print("\n  Note: Some models only support 1024x1024 size")
            print("  Try without --size flag or use --size 1024x1024\n")
        else:
            branding.print_error(f"API error: {e}")
        return 1
    except Exception as e:
        branding.print_error(f"Unexpected error: {e}")
        return 1


def is_valid_wallet_address(address: str) -> bool:
    """Validate Ethereum wallet address format."""
    if not address or not isinstance(address, str):
        return False
    if not address.startswith("0x"):
        return False
    if len(address) != 42:
        return False
    try:
        int(address[2:], 16)
        return True
    except ValueError:
        return False


def get_usdc_balance(wallet_address: str) -> Optional[float]:
    """
    Get USDC balance for a wallet address on Base chain.

    Args:
        wallet_address: Ethereum wallet address (0x...)

    Returns:
        USDC balance as float, or None if query fails
    """
    if not is_valid_wallet_address(wallet_address):
        return None

    import httpx

    # USDC contract on Base
    USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    BASE_RPC = "https://mainnet.base.org"

    try:
        # balanceOf(address) function selector: 0x70a08231
        data = {
            "jsonrpc": "2.0",
            "method": "eth_call",
            "params": [{
                "to": USDC_ADDRESS,
                "data": f"0x70a08231000000000000000000000000{wallet_address[2:]}"
            }, "latest"],
            "id": 1
        }

        with httpx.Client(timeout=10) as client:
            response = client.post(BASE_RPC, json=data)
            result = response.json().get("result", "0x0")
            # USDC has 6 decimals
            return int(result, 16) / 1e6

    except Exception:
        return None


def cmd_balance():
    """Show wallet balance."""
    if not HAS_SDK:
        branding.print_error(
            "blockrun_llm SDK not installed",
            help_link="https://github.com/blockrunai/blockrun-llm"
        )
        return 1

    if not check_environment():
        return 1

    try:
        client = LLMClient()
        wallet = client.get_wallet_address()

        # Get actual USDC balance from Base chain
        balance = get_usdc_balance(wallet)
        balance_str = f"{balance:.6f}" if balance is not None else "(unable to fetch)"

        branding.print_balance(
            wallet=wallet,
            balance=balance_str,
            network="Base"
        )

        client.close()
        return 0

    except Exception as e:
        branding.print_error(f"Error: {e}")
        return 1


def cmd_qr():
    """Show QR code for wallet funding on Base network."""
    if not HAS_SDK:
        branding.print_error(
            "blockrun_llm SDK not installed",
            help_link="https://github.com/blockrunai/blockrun-llm"
        )
        return 1

    try:
        from blockrun_llm import get_wallet_address, open_wallet_qr
        wallet = get_wallet_address()

        print()
        print(f"  Wallet: {wallet}")
        print(f"  Network: Base (Chain ID: 8453)")
        print(f"  Currency: USDC")
        print()
        print("  Opening QR code in browser...")
        print("  Scan with any wallet app to send USDC on Base.")
        print()

        open_wallet_qr(wallet)
        return 0

    except Exception as e:
        branding.print_error(f"Error: {e}")
        return 1


def cmd_solana_balance():
    """Show Solana wallet USDC balance."""
    try:
        from blockrun_llm import get_or_create_solana_wallet, get_solana_usdc_balance

        result = get_or_create_solana_wallet()
        address = result["address"]
        balance = get_solana_usdc_balance(address)
        balance_str = f"{balance:.6f}"

        branding.print_balance(
            wallet=address,
            balance=balance_str,
            network="Solana"
        )
        return 0

    except ImportError:
        branding.print_error(
            "Solana support not installed",
            help_link="https://github.com/blockrunai/blockrun-llm"
        )
        print("  Install with: pip install blockrun-llm[solana]")
        return 1
    except Exception as e:
        branding.print_error(f"Error: {e}")
        return 1


def cmd_solana_qr():
    """Show QR code for Solana wallet funding."""
    try:
        from blockrun_llm import get_or_create_solana_wallet, open_solana_wallet_qr

        result = get_or_create_solana_wallet()
        address = result["address"]

        print()
        print(f"  Wallet: {address}")
        print(f"  Network: Solana (Mainnet)")
        print(f"  Currency: USDC")
        print()
        print("  Opening QR code...")
        print("  Scan with any Solana wallet app to send USDC.")
        print()

        open_solana_wallet_qr(address)
        return 0

    except ImportError:
        branding.print_error(
            "Solana support not installed",
            help_link="https://github.com/blockrunai/blockrun-llm"
        )
        print("  Install with: pip install blockrun-llm[solana]")
        return 1
    except Exception as e:
        branding.print_error(f"Error: {e}")
        return 1


def cmd_solana_status():
    """Show Solana wallet status."""
    try:
        from scripts.wallet.solana import get_solana_wallet_status
    except ImportError:
        from wallet.solana import get_solana_wallet_status

    status = get_solana_wallet_status()

    if status["status"] == "connected":
        print()
        branding.print_success("Solana Wallet Connected")
        print(f"  Address:  {status['address']}")
        print(f"  Network:  {status['network']}")
        print(f"  Currency: {status['currency']}")
        print(f"  Explorer: {status['explorer_url']}")
        print()
    elif status["status"] == "not_installed":
        branding.print_error("Solana support not installed")
        print(f"  {status.get('help', '')}")
        print()
    else:
        branding.print_error(f"Solana wallet: {status['status']}")
        if "error" in status:
            print(f"  {status['error']}")
        if "help" in status:
            print(f"  {status['help']}")
        print()
    return 0


def cmd_solana_create():
    """Create a new Solana wallet if one doesn't exist."""
    try:
        from blockrun_llm import get_or_create_solana_wallet, generate_solana_qr_ascii

        result = get_or_create_solana_wallet()
        address = result["address"]

        if result["is_new"]:
            branding.print_success(f"New Solana wallet created!")
            print(f"  Address: {address}")
            print(f"  Explorer: https://solscan.io/account/{address}")
            print()
            print("  Fund with USDC on Solana to start using BlockRun:")
            print()
            print(generate_solana_qr_ascii(address))
            print(f"  Key stored securely in ~/.blockrun/.solana-session")
            print(f"  Your private key never leaves your machine.")
        else:
            branding.print_success(f"Solana wallet already exists")
            print(f"  Address: {address}")
            print(f"  Explorer: https://solscan.io/account/{address}")
        print()
        return 0

    except ImportError:
        branding.print_error(
            "Solana support not installed",
            help_link="https://github.com/blockrunai/blockrun-llm"
        )
        print("  Install with: pip install blockrun-llm[solana]")
        return 1
    except Exception as e:
        branding.print_error(f"Error: {e}")
        return 1


def cmd_models():
    """List available models (no wallet required)."""
    try:
        # Try to use SDK standalone functions first
        from blockrun_llm import list_models, list_image_models

        llm_models = list_models()
        image_models = list_image_models()

        if llm_models or image_models:
            branding.print_models_list(llm_models, image_models)
        else:
            branding.print_info("No models returned. Check API connection.")

        return 0

    except ImportError:
        # Fallback: direct API call if SDK not updated
        import httpx

        try:
            with httpx.Client(timeout=30) as client:
                response = client.get("https://blockrun.ai/api/v1/models")
                if response.status_code == 200:
                    models = response.json().get("data", [])
                    branding.print_models_list(models, [])
                    return 0
                else:
                    branding.print_error(f"API error: {response.status_code}")
                    return 1
        except Exception as e:
            branding.print_error(f"Could not fetch models: {e}")
            return 1

    except Exception as e:
        branding.print_error(f"Error: {e}")
        return 1


def cmd_check_update():
    """Check for plugin updates from GitHub."""
    print(f"\n  BlockRun Plugin v{__version__}")
    print("  Checking for updates...\n")

    try:
        req = urllib.request.Request(
            GITHUB_PLUGIN_URL,
            headers={"User-Agent": "BlockRun-Plugin"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            remote_plugin = json.loads(response.read().decode())
            remote_version = remote_plugin.get("version", "unknown")

        if remote_version == __version__:
            branding.print_success(f"You're up to date! (v{__version__})")
        elif remote_version > __version__:
            branding.print_info(f"Update available: v{__version__} → v{remote_version}")
            print("\n  To update, run:")
            print("    /plugin update blockrun-agent-wallet\n")
        else:
            branding.print_info(f"Local: v{__version__}, Remote: v{remote_version}")

        return 0

    except urllib.error.HTTPError as e:
        if e.code == 404:
            # Repo may be private or not yet public
            branding.print_info(f"Current version: v{__version__}")
            print("\n  To update, run:")
            print("    /plugin update blockrun-agent-wallet")
            print("\n  Or update the SDK:")
            print("    pip install --upgrade blockrun-llm\n")
            return 0
        branding.print_error(f"Could not check for updates: HTTP {e.code}")
        return 1
    except urllib.error.URLError as e:
        branding.print_error(f"Could not check for updates: {e.reason}")
        return 1
    except json.JSONDecodeError:
        branding.print_error("Invalid response from GitHub")
        return 1
    except Exception as e:
        branding.print_error(f"Error checking updates: {e}")
        return 1


def cmd_version():
    """Show current version."""
    print(f"BlockRun Plugin v{__version__}")
    return 0


def cmd_spending():
    """Show spending summary."""
    tracker = SpendingTracker()
    branding.print_spending_summary(tracker.data)
    return 0


def cmd_set_budget(amount: float):
    """Set daily budget limit."""
    tracker = SpendingTracker()
    tracker.set_budget(amount)
    branding.print_success(f"Budget set to ${amount:.2f}/day")

    # Show current status
    spent = tracker.get_total()
    remaining = amount - spent
    if remaining > 0:
        print(f"  Current spending: ${spent:.4f}")
        print(f"  Remaining today: ${remaining:.4f}")
    else:
        print(f"  Warning: Already spent ${spent:.4f} (over budget)")
    print()
    return 0


def cmd_clear_budget():
    """Remove budget limit."""
    tracker = SpendingTracker()
    tracker.clear_budget()
    branding.print_success("Budget limit removed")
    print(f"  Session spending: ${tracker.get_total():.4f} ({tracker.get_calls()} calls)")
    print()
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="blockrun-agent-wallet",
        description="BlockRun Claude Code Wallet - Access unlimited LLMs via USDC micropayments",
        epilog="""
Examples:
  %(prog)s "What is quantum computing?"
  %(prog)s "Analyze this code" --model anthropic/claude-sonnet-4
  %(prog)s "A sunset over mountains" --image
  %(prog)s --balance
  %(prog)s --models

More info: https://blockrun.ai
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Positional argument: prompt
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Prompt for chat or image generation",
    )

    # Mode flags
    parser.add_argument(
        "--image", "-i",
        action="store_true",
        help="Generate an image instead of chat",
    )
    parser.add_argument(
        "--balance", "-b",
        action="store_true",
        help="Show wallet balance",
    )
    parser.add_argument(
        "--qr",
        action="store_true",
        help="Show wallet funding QR code (Base network)",
    )

    # Solana commands
    parser.add_argument(
        "--solana-balance",
        action="store_true",
        help="Show Solana wallet USDC balance",
    )
    parser.add_argument(
        "--solana-qr",
        action="store_true",
        help="Show Solana wallet funding QR code",
    )
    parser.add_argument(
        "--solana-status",
        action="store_true",
        help="Show Solana wallet status",
    )
    parser.add_argument(
        "--solana-create",
        action="store_true",
        help="Create a new Solana wallet (if none exists)",
    )
    parser.add_argument(
        "--models", "-m",
        action="store_true",
        help="List available models with pricing",
    )
    parser.add_argument(
        "--check-update",
        action="store_true",
        help="Check for plugin updates from GitHub",
    )
    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Show plugin version",
    )

    # Budget options
    parser.add_argument(
        "--spending",
        action="store_true",
        help="Show spending summary for today",
    )
    parser.add_argument(
        "--set-budget",
        type=float,
        metavar="AMOUNT",
        help="Set daily budget limit in USD (e.g., --set-budget 1.00)",
    )
    parser.add_argument(
        "--clear-budget",
        action="store_true",
        help="Remove daily budget limit",
    )

    # Chat options
    parser.add_argument(
        "--model",
        help="Specific model ID (e.g., openai/gpt-5.2, xai/grok-3)",
    )
    parser.add_argument(
        "--system", "-s",
        help="System prompt for chat",
    )
    parser.add_argument(
        "--cheap",
        action="store_true",
        help="Use most cost-effective model",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Use fastest model",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=1024,
        help="Maximum tokens to generate (default: 1024)",
    )
    parser.add_argument(
        "--temperature", "-t",
        type=float,
        help="Sampling temperature (0.0-2.0)",
    )

    # Image options
    parser.add_argument(
        "--size",
        default="1024x1024",
        help="Image size (default: 1024x1024)",
    )

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if args.version:
        return cmd_version()

    if args.check_update:
        return cmd_check_update()

    if args.balance:
        return cmd_balance()

    if args.qr:
        return cmd_qr()

    if args.solana_balance:
        return cmd_solana_balance()

    if args.solana_qr:
        return cmd_solana_qr()

    if args.solana_status:
        return cmd_solana_status()

    if args.solana_create:
        return cmd_solana_create()

    if args.models:
        return cmd_models()

    if args.spending:
        return cmd_spending()

    if args.set_budget is not None:
        return cmd_set_budget(args.set_budget)

    if args.clear_budget:
        return cmd_clear_budget()

    if not args.prompt:
        parser.print_help()
        return 1

    if args.image:
        return cmd_image(
            prompt=args.prompt,
            model=args.model,
            size=args.size,
        )

    return cmd_chat(
        prompt=args.prompt,
        model=args.model,
        system=args.system,
        cheap=args.cheap,
        fast=args.fast,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
    )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n  Interrupted by user")
        sys.exit(130)
