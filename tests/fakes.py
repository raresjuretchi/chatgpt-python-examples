"""Tiny stand-ins for the OpenAI client so tests run offline without an API key."""
from types import SimpleNamespace


def response(output_text="", output=(), id_="resp_1"):
    return SimpleNamespace(id=id_, output_text=output_text, output=list(output))


def function_call(call_id, name, arguments):
    return SimpleNamespace(type="function_call", call_id=call_id, name=name, arguments=arguments)


def message_item(text):
    return SimpleNamespace(type="message", content=[SimpleNamespace(type="output_text", text=text)])


def delta(text):
    return SimpleNamespace(type="response.output_text.delta", delta=text)


class FakeResponses:
    def __init__(self, replies=()):
        self.replies = list(replies)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        reply = self.replies.pop(0)
        return iter(reply) if kwargs.get("stream") else reply


class FakeClient:
    def __init__(self, replies=()):
        self.responses = FakeResponses(replies)
