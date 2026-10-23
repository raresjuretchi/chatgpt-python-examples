import json
from types import SimpleNamespace

import pytest

from chatgpt_examples import chat, function_calling, hello, stream
from tests.fakes import FakeClient, delta, function_call, message_item, response


def test_hello_returns_output_text():
    client = FakeClient([response("Hi!")])
    assert hello.ask(client, "hello", model="m") == "Hi!"
    assert client.responses.calls[0] == {"model": "m", "input": "hello"}


def test_stream_joins_text_deltas_and_ignores_other_events():
    events = [SimpleNamespace(type="response.created"), delta("Hel"), delta("lo"),
              SimpleNamespace(type="response.completed")]
    client = FakeClient([events])
    assert stream.stream_reply(client, "hi", out=lambda *a, **k: None) == "Hello"


def test_stream_raises_on_error_event():
    client = FakeClient([[SimpleNamespace(type="error", message="boom")]])
    with pytest.raises(RuntimeError, match="boom"):
        stream.stream_reply(client, "hi", out=lambda *a, **k: None)


def test_conversation_chains_previous_response_id():
    client = FakeClient([response("one", id_="r1"), response("two", id_="r2")])
    convo = chat.Conversation(client)
    assert convo.send("first") == "one"
    assert convo.send("second") == "two"
    calls = client.responses.calls
    assert "previous_response_id" not in calls[0]
    assert calls[1]["previous_response_id"] == "r1"
    assert calls[1]["instructions"] == chat.INSTRUCTIONS


@pytest.mark.parametrize("expr,expected", [("250 * 1.08 * 1.21", 326.7), ("2,000 / 8", 250), ("-3 ** 2", -9)])
def test_calculate(expr, expected):
    assert function_calling.calculate(expr) == pytest.approx(expected)


@pytest.mark.parametrize("expr", ["__import__('os')", "x + 1", "9 ** 999"])
def test_calculate_rejects_unsafe_input(expr):
    with pytest.raises(ValueError):
        function_calling.calculate(expr)


def test_function_loop_sends_outputs_back():
    client = FakeClient([
        response(output=[function_call("c1", "calculate", json.dumps({"expression": "250 * 1.08"}))], id_="r1"),
        response("That is 270 USD.", output=[message_item("That is 270 USD.")], id_="r2"),
    ])
    answer = function_calling.run(client, "250 EUR in USD at 1.08?", log=lambda *_: None)
    assert answer == "That is 270 USD."

    second = client.responses.calls[1]
    assert second["previous_response_id"] == "r1"
    output = second["input"][0]
    assert output["type"] == "function_call_output" and output["call_id"] == "c1"
    assert json.loads(output["output"])["result"] == pytest.approx(270)


def test_function_errors_are_returned_as_json():
    result = json.loads(function_calling.run_function("current_time", json.dumps({"timezone": "Nope/Nope"})))
    assert "error" in result


def test_function_loop_gives_up_after_max_rounds():
    looping = response(output=[function_call("c", "calculate", '{"expression": "1+1"}')])
    client = FakeClient([looping] * 4)
    with pytest.raises(RuntimeError):
        function_calling.run(client, "loop", max_rounds=3, log=lambda *_: None)
