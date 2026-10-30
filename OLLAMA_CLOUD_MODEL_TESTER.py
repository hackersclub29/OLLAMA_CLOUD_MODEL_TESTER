
import os
import sys
import time
import requests

from pathlib import Path
from getpass import getpass
from datetime import datetime
from ollama import Client


# ─────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────

TOOL_NAME = "OLLAMA CLOUD MODEL TESTER"
VERSION = "3.0"

KEY_FILE = Path(__file__).resolve().parent / ".ollama_api_key"

TEST_PROMPT = [
    {
        "role": "user",
        "content": "Reply with only the word: WORKING",
    }
]

EXPECTED_RESPONSE = "WORKING"

MAX_RETRIES = 1
REQUEST_TIMEOUT = 60

SKIP_KEYWORDS = [
    "requires a subscription",
    "subscription required",
    "upgrade your plan",
    "not available",
    "unauthorized",
    "access denied",
    "payment required",
    "quota exceeded",
    "billing",
    "insufficient credits",
]

RETRY_KEYWORDS = [
    "timeout",
    "timed out",
    "connection",
    "temporarily unavailable",
    "server error",
    "502",
    "503",
    "504",
]


# ─────────────────────────────────────────
#  TERMINAL COLORS
# ─────────────────────────────────────────

COLOR_ENABLED = sys.stdout.isatty()

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"


# ─────────────────────────────────────────
#  GRADIENT TEXT
# ─────────────────────────────────────────

def gradient_text(text):

    if not COLOR_ENABLED:
        return text

    colors = [
        (0, 220, 255),
        (50, 130, 255),
        (160, 70, 255),
        (255, 50, 180),
    ]

    output = ""

    for i, char in enumerate(text):

        ratio = i / max(len(text) - 1, 1)

        position = ratio * (len(colors) - 1)

        index = int(position)

        fraction = position - index

        if index >= len(colors) - 1:

            r, g, b = colors[-1]

        else:

            start = colors[index]
            end = colors[index + 1]

            r = int(start[0] + (end[0] - start[0]) * fraction)
            g = int(start[1] + (end[1] - start[1]) * fraction)
            b = int(start[2] + (end[2] - start[2]) * fraction)

        output += f"\033[38;2;{r};{g};{b}m{char}"

    return output + RESET


# ─────────────────────────────────────────
#  ANIMATED BANNER
# ─────────────────────────────────────────

def show_banner():

    if COLOR_ENABLED:

        print("\033[2J\033[H", end="")

    width = 64

    top = "╔" + "═" * width + "╗"
    bottom = "╚" + "═" * width + "╝"

    lines = [
        top,
        "║" + " " * width + "║",
        "║" + "OLLAMA CLOUD".center(width) + "║",
        "║" + "MODEL TESTER".center(width) + "║",
        "║" + " " * width + "║",
        "║" + "DYNAMIC MODEL AVAILABILITY & RESPONSE TESTING".center(width) + "║",
        "║" + f"VERSION {VERSION}".center(width) + "║",
        "║" + " " * width + "║",
        bottom,
    ]

    print()

    for line in lines:

        print(gradient_text(line))

        if COLOR_ENABLED:
            time.sleep(0.06)

    print()

    print(
        f"{DIM}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}"
        if COLOR_ENABLED else
        f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # Animated initialization bar

    if COLOR_ENABLED:

        print("\n⚡ Initializing tool...")

        for i in range(21):

            bar = "█" * i + "░" * (20 - i)

            percentage = i * 5

            print(
                f"\r{CYAN}[{bar}] {percentage:3d}%{RESET}",
                end="",
                flush=True
            )

            time.sleep(0.035)

        print("\n")

    else:

        print("\nInitializing tool...\n")


# ─────────────────────────────────────────
#  SAVE API KEY
# ─────────────────────────────────────────

def save_api_key(api_key):

    try:

        KEY_FILE.write_text(
            api_key.strip(),
            encoding="utf-8"
        )

        # Restrict file permissions on Unix-like systems.

        if os.name != "nt":

            KEY_FILE.chmod(0o600)

        print(f"\n✅ API KEY saved: {KEY_FILE.name}")

        return True

    except OSError as e:

        print(f"\n❌ Failed to save API KEY: {e}")

        return False


# ─────────────────────────────────────────
#  GET API KEY
# ─────────────────────────────────────────

def obtain_api_key():

    # Check environment variable first.

    env_key = os.getenv("OLLAMA_API_KEY")

    if env_key and env_key.strip():

        print("🔑 Found API KEY in environment variable.")

        api_key = env_key.strip()

    else:

        api_key = None

        # Check previously saved API key.

        if KEY_FILE.exists():

            try:

                saved_key = KEY_FILE.read_text(
                    encoding="utf-8"
                ).strip()

                if saved_key:

                    print("🔐 Previously saved API KEY found.")

                    choice = input(
                        "Use saved API KEY? [Y/n]: "
                    ).strip().lower()

                    if choice in ("", "y", "yes"):

                        api_key = saved_key

                        print("✅ Using saved API KEY.")

            except OSError as e:

                print(f"⚠️ Could not read saved API KEY: {e}")

        # Request a new API key if necessary.

        if not api_key:

            api_key = getpass(
                "\n🔑 Enter Ollama Cloud API KEY: "
            ).strip()

    if not api_key:

        print("❌ API KEY cannot be empty.")

        sys.exit(1)

    # Ask whether to save the supplied key.

    save_choice = input(
        "\n💾 Save API KEY in tool directory for future use? [y/N]: "
    ).strip().lower()

    if save_choice in ("y", "yes"):

        save_api_key(api_key)

    else:

        print("ℹ️ API KEY will not be saved.")

    return api_key


# ─────────────────────────────────────────
#  INITIALIZE CLIENT
# ─────────────────────────────────────────

def initialize_client(api_key):

    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
    }

    try:

        client = Client(
            host="https://ollama.com",
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )

        return client, headers

    except Exception as e:

        print(f"❌ Client initialization failed: {e}")

        sys.exit(1)


# ─────────────────────────────────────────
#  RESPONSE FIELD HANDLER
# ─────────────────────────────────────────

def get_field(data, field, default=None):

    if isinstance(data, dict):

        return data.get(field, default)

    return getattr(data, field, default)


# ─────────────────────────────────────────
#  CHECK RESTRICTIONS
# ─────────────────────────────────────────

def is_restricted(message):

    message = str(message).lower()

    return any(
        keyword in message
        for keyword in SKIP_KEYWORDS
    )


# ─────────────────────────────────────────
#  FETCH MODELS DYNAMICALLY
# ─────────────────────────────────────────

def fetch_models(headers):

    print(
        f"{CYAN}📡 Fetching models from "
        f"https://ollama.com/api/tags ...{RESET}"
        if COLOR_ENABLED else
        "📡 Fetching models from https://ollama.com/api/tags ..."
    )

    try:

        response = requests.get(
            "https://ollama.com/api/tags",
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        models = [
            model.get("name")
            for model in data.get("models", [])
            if isinstance(model, dict) and model.get("name")
        ]

        models = list(dict.fromkeys(models))

        print(f"✅ Found {len(models)} models.\n")

        return models

    except requests.exceptions.HTTPError as e:

        response = e.response

        status = response.status_code if response is not None else "Unknown"

        print(f"❌ HTTP Error: {status}")

        if response is not None:

            print(response.text[:500])

        sys.exit(1)

    except requests.exceptions.RequestException as e:

        print(f"❌ Failed to fetch models: {e}")

        sys.exit(1)

    except (ValueError, AttributeError, TypeError) as e:

        print(f"❌ Failed to parse model list: {e}")

        sys.exit(1)


# ─────────────────────────────────────────
#  TEST A SINGLE MODEL
# ─────────────────────────────────────────

def test_model(model_name, client, working, skipped, failed):

    print(f"\n{'─' * 60}")

    print(f"🔍 Testing : {model_name}")

    print(f"{'─' * 60}")

    for attempt in range(MAX_RETRIES + 1):

        response_text = ""

        tokens_per_second = None

        start_time = time.perf_counter()

        try:

            for part in client.chat(
                model=model_name,
                messages=TEST_PROMPT,
                stream=True
            ):

                message = get_field(
                    part,
                    "message",
                    {}
                )

                chunk = get_field(
                    message,
                    "content",
                    ""
                )

                if chunk:

                    response_text += chunk

                    print(
                        chunk,
                        end="",
                        flush=True
                    )

                # Detect restrictions during streaming.

                if is_restricted(response_text):

                    latency = time.perf_counter() - start_time

                    print("\n⚠️ RESTRICTED — Subscription or access required")

                    skipped.append(model_name)

                    return {
                        "model": model_name,
                        "status": "RESTRICTED",
                        "latency": round(latency, 3),
                        "tokens_per_second": None
                    }

                # Collect generation statistics.

                if get_field(part, "done", False):

                    eval_count = get_field(
                        part,
                        "eval_count",
                        None
                    )

                    eval_duration = get_field(
                        part,
                        "eval_duration",
                        None
                    )

                    if eval_count and eval_duration:

                        duration = eval_duration / 1_000_000_000

                        if duration > 0:

                            tokens_per_second = round(
                                eval_count / duration,
                                2
                            )

            latency = time.perf_counter() - start_time

            print()

            # Normalize response.

            normalized_response = (
                response_text.strip()
                .upper()
                .strip(" \t\r\n.!?\"'`")
            )

            # Validate model output.

            if normalized_response == EXPECTED_RESPONSE:

                print("✅ WORKING")

                working.append(model_name)

                print(f"⏱️ Response Time : {latency:.3f} seconds")

                if tokens_per_second is not None:

                    print(
                        f"⚡ Generation Speed : "
                        f"{tokens_per_second} tokens/sec"
                    )

                return {
                    "model": model_name,
                    "status": "WORKING",
                    "latency": round(latency, 3),
                    "tokens_per_second": tokens_per_second
                }

            else:

                error = "Unexpected response from model."

                print(f"❌ FAILED — {error}")

                print(f"⏱️ Response Time : {latency:.3f} seconds")

                failed.append((model_name, error))

                return {
                    "model": model_name,
                    "status": "FAILED",
                    "latency": round(latency, 3),
                    "tokens_per_second": tokens_per_second,
                    "error": error
                }

        except Exception as e:

            error_message = str(e)

            error_lower = error_message.lower()

            status_code = getattr(e, "status_code", None)

            latency = time.perf_counter() - start_time

            # Check authentication, billing and quota restrictions.

            if (
                status_code in (401, 402, 403, 429)
                or is_restricted(error_message)
            ):

                print(f"\n⚠️ RESTRICTED — {error_message}")

                skipped.append(model_name)

                return {
                    "model": model_name,
                    "status": "RESTRICTED",
                    "latency": round(latency, 3),
                    "tokens_per_second": None,
                    "error": error_message
                }

            # Retry temporary failures.

            retryable = (
                status_code in (500, 502, 503, 504)
                or any(
                    keyword in error_lower
                    for keyword in RETRY_KEYWORDS
                )
            )

            if retryable and attempt < MAX_RETRIES:

                print(
                    f"\n🔄 Temporary error. "
                    f"Retrying ({attempt + 1}/{MAX_RETRIES})..."
                )

                time.sleep(2)

                continue

            # Record final failure.

            print(f"\n❌ FAILED — {error_message}")

            failed.append(
                (model_name, error_message)
            )

            return {
                "model": model_name,
                "status": "FAILED",
                "latency": round(latency, 3),
                "tokens_per_second": None,
                "error": error_message
            }


# ─────────────────────────────────────────
#  FINAL RESULTS REPORT
# ─────────────────────────────────────────

def print_report(working, skipped, failed, total, results):

    print("\n")

    print("╔" + "═" * 58 + "╗")

    print(
        "║" +
        "       📋 FINAL RESULTS REPORT".center(58) +
        "║"
    )

    print("╚" + "═" * 58 + "╝")

    # Working models.

    print(f"\n✅ WORKING MODELS ({len(working)}):")

    if working:

        for i, model in enumerate(working, 1):

            print(f"    {i:02d}. {model}")

    else:

        print("    None")

    # Restricted models.

    print(f"\n⚠️ RESTRICTED MODELS ({len(skipped)}):")

    if skipped:

        for i, model in enumerate(skipped, 1):

            print(f"    {i:02d}. {model}")

    else:

        print("    None")

    # Failed models.

    print(f"\n❌ FAILED MODELS ({len(failed)}):")

    if failed:

        for i, (model, error) in enumerate(failed, 1):

            print(f"    {i:02d}. {model}")

            print(f"         ↳ {error}")

    else:

        print("    None")

    # Performance metrics.

    successful = [
        result
        for result in results
        if result["status"] == "WORKING"
    ]

    if successful:

        avg_latency = sum(
            result["latency"]
            for result in successful
        ) / len(successful)

        speeds = [
            result["tokens_per_second"]
            for result in successful
            if result["tokens_per_second"] is not None
        ]

        print("\n📊 PERFORMANCE SUMMARY")

        print(f"    Average Latency : {avg_latency:.3f} seconds")

        if speeds:

            avg_speed = sum(speeds) / len(speeds)

            print(f"    Average Speed   : {avg_speed:.2f} tokens/sec")

    # Final statistics.

    print("\n" + "─" * 60)

    print(f"  Total Fetched : {total}")

    print(f"  ✅ Working    : {len(working)}")

    print(f"  ⚠️ Restricted: {len(skipped)}")

    print(f"  ❌ Failed     : {len(failed)}")

    print("─" * 60)

    print("\n✅ TESTING COMPLETED.")


# ─────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────

def main():

    # Display animated banner.

    show_banner()

    # Obtain API key.

    API_KEY = obtain_api_key()

    # Initialize client.

    client, headers = initialize_client(API_KEY)

    print("\n" + "─" * 60)

    print("🚀 STARTING OLLAMA CLOUD MODEL TESTER")

    print("─" * 60)

    # Dynamically fetch models.

    MODELS = fetch_models(headers)

    if not MODELS:

        print("❌ No models found.")

        sys.exit(1)

    # Display available models.

    print("📦 MODELS TO TEST:")

    for i, model in enumerate(MODELS, 1):

        print(f"    {i:02d}. {model}")

    # Initialize result collections.

    working_models = []

    skipped_models = []

    failed_models = []

    all_results = []

    print("\n" + "═" * 60)

    print("             STARTING MODEL TESTS")

    print("═" * 60)

    # Test every model sequentially.

    try:

        for model in MODELS:

            result = test_model(
                model,
                client,
                working_models,
                skipped_models,
                failed_models
            )

            if result is not None:

                all_results.append(result)

    except KeyboardInterrupt:

        print("\n\n⚠️ Testing interrupted by user.")

    # Display terminal report only.

    print_report(
        working_models,
        skipped_models,
        failed_models,
        len(MODELS),
        all_results
    )


# ─────────────────────────────────────────
#  EXECUTION
# ─────────────────────────────────────────

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print("\n\n⚠️ Tool terminated by user.")

    except Exception as e:

        print(f"\n❌ Unexpected error: {e}")

    finally:

        print("\n👋 Ollama Cloud Model Tester exited.")
