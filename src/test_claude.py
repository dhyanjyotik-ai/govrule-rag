import os
from dotenv import load_dotenv
import anthropic

load_dotenv()
key = os.environ.get("ANTHROPIC_API_KEY", "")
if not key or key == "placeholder":
    raise SystemExit("No real API key found in .env")

client = anthropic.Anthropic()
reply = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=50,
    messages=[{"role": "user", "content": "Reply with the single word: ready"}],
)
print(reply.content[0].text)