"""
SocialClaw Branding Utilities - Consistent CLI output formatting.

Provides branded headers, footers, and response formatting for all SocialClaw
CLI operations, ensuring a professional and recognizable user experience.
"""

from typing import Optional
import sys


class BlockRunBranding:
    """Unified branding output system for SocialClaw."""

    # Compact ASCII logo for CLI
    LOGO = """
 ____             _       _  ____ _
/ ___|  ___   ___(_) __ _| |/ ___| | __ ___      __
\\___ \\ / _ \\ / __| |/ _` | | |   | |/ _` \\ \\ /\\ / /
 ___) | (_) | (__| | (_| | | |___| | (_| |\\ V  V /
|____/ \\___/ \\___|_|\\__,_|_|\\____|_|\\__,_| \\_/\\_/
                                    SOCIALCLAW"""

    # Simple header for regular operations
    HEADER_LINE = "=" * 60

    # Brand colors (ANSI codes for terminal)
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "blue": "\033[94m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "cyan": "\033[96m",
        "dim": "\033[2m",
    }

    def __init__(self, use_color: bool = True, show_logo: bool = False):
        """
        Initialize branding utilities.

        Args:
            use_color: Whether to use ANSI color codes (default: True)
            show_logo: Whether to show full logo (default: False for compact output)
        """
        self.use_color = use_color and sys.stdout.isatty()
        self.show_logo = show_logo

    def _c(self, color: str, text: str) -> str:
        """Apply color if enabled."""
        if not self.use_color:
            return text
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"

    def print_header(
        self,
        model: str,
        wallet: Optional[str] = None,
        balance: Optional[str] = None,
        cost_estimate: Optional[str] = None,
    ):
        """
        Print branded header before operation.

        Args:
            model: Model being used
            wallet: Wallet address (truncated)
            balance: Current USDC balance
            cost_estimate: Estimated cost for this operation
        """
        if self.show_logo:
            print(self._c("cyan", self.LOGO))
            print()

        print(self._c("dim", self.HEADER_LINE))
        print(self._c("bold", "  SOCIALCLAW"))
        print(self._c("dim", self.HEADER_LINE))

        # Model info
        print(f"  Model: {self._c('cyan', model)}", end="")
        if cost_estimate:
            print(f"  |  Est. Cost: {self._c('yellow', cost_estimate)}", end="")
        print()

        # Wallet info
        if wallet:
            wallet_display = f"{wallet[:6]}...{wallet[-4:]}" if len(wallet) > 12 else wallet
            print(f"  Wallet: {self._c('dim', wallet_display)}", end="")
            if balance:
                print(f"  |  Balance: {self._c('green', balance)} USDC", end="")
            print()

        print(self._c("dim", self.HEADER_LINE))
        print()

    def print_response(self, content: str):
        """Print the main response content."""
        print(content)

    def print_model_attribution(self, model: str, description: str = None):
        """
        Print model attribution after response.

        Args:
            model: Model ID used (e.g., "openai/gpt-5.2")
            description: Optional model description
        """
        print()
        print(self._c("dim", "-" * 60))

        # Parse provider from model ID
        provider = model.split("/")[0].upper() if "/" in model else "Unknown"
        model_name = model.split("/")[1] if "/" in model else model

        # Format model name nicely (keep version numbers intact)
        display_name = model_name.upper().replace("-", " ")

        print(f"  {self._c('cyan', 'Reviewed by:')} {display_name} ({provider})")

        if description:
            print(f"  {self._c('dim', description)}")

        print(f"  {self._c('dim', 'Accessed via: SocialClaw x402 micropayments')}")
        print(self._c("dim", "-" * 60))

    def print_footer(
        self,
        actual_cost: Optional[str] = None,
        new_balance: Optional[str] = None,
        session_total: Optional[float] = None,
        session_calls: Optional[int] = None,
        budget_remaining: Optional[float] = None,
        budget_limit: Optional[float] = None,
    ):
        """
        Print branded footer after operation.

        Args:
            actual_cost: Actual cost of the operation
            new_balance: New wallet balance after operation
            session_total: Total spent this session
            session_calls: Number of calls this session
            budget_remaining: Remaining budget (None if no limit)
            budget_limit: Budget limit (None if no limit)
        """
        print()
        print(self._c("dim", "-" * 60))

        if actual_cost:
            print(f"  {self._c('green', '✓')} This call: ${actual_cost}")

        if session_total is not None:
            calls_str = f" ({session_calls} calls)" if session_calls else ""
            print(f"  {self._c('green', '✓')} Session total: ${session_total:.4f}{calls_str}")

        if budget_remaining is not None and budget_limit is not None:
            print(f"  {self._c('green', '✓')} Budget remaining: ${budget_remaining:.4f} of ${budget_limit:.2f}")

        print(f"  {self._c('dim', 'Powered by SocialClaw × BlockRun • blockrun.ai')}")

    def print_error(self, message: str, help_link: Optional[str] = None):
        """
        Print branded error message.

        Args:
            message: Error message
            help_link: Optional help URL
        """
        print()
        print(self._c("red", f"  Error: {message}"))
        if help_link:
            print(f"  Help: {self._c('cyan', help_link)}")
        print()

    def print_success(self, message: str):
        """Print branded success message."""
        print(self._c("green", f"  ✓ {message}"))

    def print_info(self, message: str):
        """Print branded info message."""
        print(self._c("cyan", f"  ℹ {message}"))

    def print_balance(self, wallet: str, balance: str, network: str = "Base"):
        """
        Print wallet balance in branded format.

        Args:
            wallet: Full wallet address
            balance: USDC balance
            network: Network name (default: Base)
        """
        print()
        print(self._c("dim", self.HEADER_LINE))
        print(self._c("bold", "  SOCIALCLAW WALLET"))
        print(self._c("dim", self.HEADER_LINE))
        print(f"  Address: {self._c('cyan', wallet)}")
        print(f"  Network: {network}")
        print(f"  Balance: {self._c('green', balance)} USDC")
        print(self._c("dim", self.HEADER_LINE))
        print()

    def print_models_list(self, models: list, image_models: list = None):
        """
        Print available models in branded format with pricing.

        Args:
            models: List of LLM model dicts with id, pricing info
            image_models: Optional list of image model dicts
        """
        print()
        print(self._c("dim", self.HEADER_LINE))
        print(self._c("bold", "  AVAILABLE MODELS"))
        print(self._c("dim", self.HEADER_LINE))
        print()
        print(f"  {self._c('dim', 'Live data from:')} {self._c('cyan', 'https://blockrun.ai/api/pricing')}")
        print()

        # LLM Models
        if models:
            print(self._c("bold", "  Chat Models:"))
            print()
            for model in models:
                model_id = model.get("id", "unknown")
                # Handle different pricing formats from API
                input_price = model.get("inputPrice") or model.get("pricing", {}).get("input")
                output_price = model.get("outputPrice") or model.get("pricing", {}).get("output")

                print(f"    {self._c('cyan', model_id)}")
                if input_price is not None and output_price is not None:
                    print(f"      ${input_price}/M in, ${output_price}/M out")
                print()

        # Image Models
        if image_models:
            print(self._c("bold", "  Image Models:"))
            print()
            for model in image_models:
                model_id = model.get("id", "unknown")
                price = model.get("pricePerImage")

                print(f"    {self._c('cyan', model_id)}")
                if price is not None:
                    print(f"      ${price}/image")
                print()

        print(self._c("dim", self.HEADER_LINE))
        print(f"  {self._c('dim', 'Prices in USDC • Pay only for what you use')}")
        print()


    def print_budget_error(self, spent: float, limit: float, calls: int):
        """
        Print budget limit reached error.

        Args:
            spent: Amount spent
            limit: Budget limit
            calls: Number of calls made
        """
        print()
        print(self._c("dim", self.HEADER_LINE))
        print(self._c("yellow", "  ⚠ BUDGET LIMIT REACHED"))
        print(self._c("dim", self.HEADER_LINE))
        print(f"  Spent: {self._c('red', f'${spent:.4f}')} across {calls} calls")
        print(f"  Limit: ${limit:.2f}/day")
        print()
        print("  Options:")
        print(f"    {self._c('cyan', 'python run.py --set-budget 2.00')}   # Increase limit")
        print(f"    {self._c('cyan', 'python run.py --clear-budget')}      # Remove limit")
        print(f"    {self._c('dim', '(Budget resets tomorrow)')}")
        print()

    def print_spending_summary(self, data: dict):
        """
        Print spending summary.

        Args:
            data: Spending tracker data dict
        """
        spending = data.get("spending", {})
        total = spending.get("total_usd", 0.0)
        calls = spending.get("calls", 0)
        limit = data.get("budget_limit")
        history = data.get("history", [])
        session_id = data.get("session_id", "today")

        print()
        print(self._c("dim", self.HEADER_LINE))
        print(self._c("bold", "  SPENDING SUMMARY"))
        print(self._c("dim", self.HEADER_LINE))
        print(f"  Date: {session_id}")
        print(f"  Spent: {self._c('cyan', f'${total:.4f}')} across {calls} calls")

        if limit is not None:
            remaining = max(0, limit - total)
            print(f"  Budget: ${limit:.2f} ({self._c('green', f'${remaining:.4f}')} remaining)")
        else:
            print(f"  Budget: {self._c('dim', 'No limit set')}")

        if history:
            print()
            print(self._c("bold", "  Recent calls:"))
            for entry in history[-10:]:
                ts = entry.get("timestamp", "")
                time_str = ts[11:16] if len(ts) >= 16 else ts  # Extract HH:MM
                model = entry.get("model", "unknown")
                cost = entry.get("cost", 0)
                # Truncate long model names to avoid misalignment
                model_display = model[:32] + "..." if len(model) > 35 else model
                print(f"    {time_str}  {model_display:<35}  ${cost:.4f}")

        print(self._c("dim", self.HEADER_LINE))
        print()


# Singleton instance for easy import
branding = BlockRunBranding()
