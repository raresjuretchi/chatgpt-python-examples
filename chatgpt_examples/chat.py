"""Multi-turn chat in the terminal.

The Responses API can keep the conversation server-side: each turn passes
`previous_response_id`, so the script only sends the new user message.

    python -m chatgpt_examples.chat
Type 'exit' or press Ctrl+D to quit.
"""
from chatgpt_examples.common import DEFAULT_MODEL, get_client

INSTRUCTIONS = "You are a concise, friendly assistant. Prefer short answers unless asked for detail."


class Conversation:
    def __init__(self, client, model: str = DEFAULT_MODEL, instructions: str = INSTRUCTIONS):
        self.client = client
        self.model = model
        self.instructions = instructions
        self.last_id: str | None = None

    def send(self, user_text: str) -> str:
        kwargs = {"model": self.model, "instructions": self.instructions, "input": user_text}
        if self.last_id:
            kwargs["previous_response_id"] = self.last_id
        response = self.client.responses.create(**kwargs)
        self.last_id = response.id
        return response.output_text


def main() -> None:
    chat = Conversation(get_client())
    print(f"Chatting with {chat.model}. Type 'exit' to quit.")
    while True:
        try:
            user = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user.lower() in {"exit", "quit"}:
            break
        if user:
            print(f"\nassistant> {chat.send(user)}")


if __name__ == "__main__":
    main()
