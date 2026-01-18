from anthropic import Anthropic
ANTHROPIC_API_KEY = "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"

client = Anthropic(api_key=ANTHROPIC_API_KEY)

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello! How are you?"}
    ]
)

# Extract just the text
text = message.content[0].text
print(text)  # Clean output!