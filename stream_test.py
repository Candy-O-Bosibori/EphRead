# ============================================================
# Async Streaming Anthropic API Call
# ============================================================
#
# SYNC vs ASYNC — what's the difference?
#
# SYNC (old way):                    ASYNC (new way):
# ─────────────────────────────────  ─────────────────────────────────
# client = Anthropic()               client = AsyncAnthropic()
# with client.messages.stream(...)   async with client.messages.stream(...)
# for text in stream.text_stream:    async for text in stream.text_stream:
#   print(text)                        print(text)
#                                    asyncio.run(main())
#
# WHY ASYNC MATTERS:
# • Sync: While Claude thinks, your whole program freezes and waits.
#   If 100 users hit your app, user 2 waits for user 1 to finish.
# • Async: While Claude thinks for user 1, your app handles users
#   2, 3, 4... at the same time. No one waits unnecessarily.
# • FastAPI (Task 2) is built on async — this is the right foundation.
# ============================================================

import os       # For environment variables
import asyncio  # Built into Python — gives us async/await superpowers
import anthropic

# Load API key from .env file (same as before)
env_path = os.path.join(os.path.dirname(__file__), ".env")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ[key] = value

# ── async def main() ──────────────────────────────────────────────────
# "async def" marks this as an async function.
# Inside it, we can use "await" and "async with/for".
async def main():

    # AsyncAnthropic is the async version of Anthropic()
    # It can handle multiple requests at the same time without blocking.
    client = anthropic.AsyncAnthropic()

    print("Streaming response:\n")

    # "async with" is like "with" but async-friendly.
    # It opens the streaming connection without freezing the program.
    async with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[
            {"role": "user", "content": "Tell me a fun fact about the ocean."}
        ],
    ) as stream:

        # "async for" is like "for" but async-friendly.
        # It receives each chunk without blocking other work.
        async for text in stream.text_stream:
            print(text, end="", flush=True)

    # "await" means: pause here until get_final_message() finishes,
    # but let other async tasks run in the meantime (if there were any).
    final_message = await stream.get_final_message()

    print("\n\n--- Token Usage ---")
    print(f"Input tokens:  {final_message.usage.input_tokens}")
    print(f"Output tokens: {final_message.usage.output_tokens}")


# asyncio.run() starts the async engine and runs our main() function.
# Every async program needs this as its entry point.
asyncio.run(main())
