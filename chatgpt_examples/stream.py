"""Stream the reply as it is generated.

    python -m chatgpt_examples.stream "Write a limerick about Kubernetes"
"""
from chatgpt_examples.common import DEFAULT_MODEL, get_client, prompt_from_args


def stream_reply(client, prompt: str, model: str = DEFAULT_MODEL, out=print) -> str:
    chunks = []
    for event in client.responses.create(model=model, input=prompt, stream=True):
        if event.type == "response.output_text.delta":
            chunks.append(event.delta)
            out(event.delta, end="", flush=True)
        elif event.type == "error":
            raise RuntimeError(getattr(event, "message", "stream error"))
    out()
    return "".join(chunks)


def main() -> None:
    stream_reply(get_client(), prompt_from_args("Write a short poem about a sunrise over the sea."))


if __name__ == "__main__":
    main()
