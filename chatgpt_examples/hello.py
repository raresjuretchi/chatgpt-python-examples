"""Send one request with the Responses API and print the reply.

    python -m chatgpt_examples.hello "Explain vector databases in two sentences"
"""
from chatgpt_examples.common import DEFAULT_MODEL, get_client, prompt_from_args


def ask(client, prompt: str, model: str = DEFAULT_MODEL) -> str:
    response = client.responses.create(model=model, input=prompt)
    return response.output_text


def main() -> None:
    print(ask(get_client(), prompt_from_args("Say hello and share one surprising fact about honeybees.")))


if __name__ == "__main__":
    main()
