import pytest
import os
from agogosml.writer.output_writer import OutputWriter
from agogosml.writer.output_writer_factory import OutputWriterFactory
from agogosml.common.flask_http_listener_client import FlaskHttpListenerClient
from agogosml.common.kafka_streaming_client import KafkaStreamingClient
from agogosml.common.eventhub_streaming_client import EventHubStreamingClient
from .client_mocks import StreamingClientMock, HttpClientMock


@pytest.fixture
def mock_streaming_client():
    return StreamingClientMock()


@pytest.fixture
def mock_listener_client():
    return HttpClientMock(0)


def test_when_ctor_instance_created(mock_streaming_client, mock_listener_client):
    ow = OutputWriter(mock_streaming_client, mock_listener_client)
    assert ow is not None


def test_on_message_received_sent_called(mock_streaming_client,
                                         mock_listener_client):
    ow = OutputWriter(mock_streaming_client, mock_listener_client)
    ow.on_message_received('test')
    assert mock_streaming_client.get_sent()


def test_on_listener_event_sent_called(mock_streaming_client,
                                       mock_listener_client):
    ow = OutputWriter(mock_streaming_client, mock_listener_client)
    ow.start_incoming_messages()
    mock_listener_client.mock_new_incoming_message()
    assert mock_streaming_client.get_sent()
    assert mock_listener_client.get_started()


def test_when_failed_to_send_then_report_error(mock_streaming_client, mock_listener_client):
    # arrange
    ow = OutputWriter(mock_streaming_client, mock_listener_client)
    ow.start_incoming_messages()
    mock_streaming_client.set_fail_send(True)
    # act
    result = mock_listener_client.mock_new_incoming_message()
    # assert
    assert result is False


def test_on_stop_event_stop_called(mock_streaming_client, mock_listener_client):
    ow = OutputWriter(mock_streaming_client, mock_listener_client)
    ow.start_incoming_messages()
    ow.stop_incoming_messages()
    assert mock_listener_client.get_stopped()


def test_when_unknown_client_throw():
    config = {'client': {'type': 'aaa'}}
    with pytest.raises(Exception):
        OutputWriterFactory.create(config)


@pytest.mark.integration
def test_output_writer_factory_event_hub():

    config = {
        'client': {
            'type': 'eventhub',
            'config': {
                'EVENT_HUB_NAMESPACE': os.getenv("EVENT_HUB_NAMESPACE"),
                'EVENT_HUB_NAME': os.getenv("EVENT_HUB_NAME"),
                'EVENT_HUB_SAS_POLICY': os.getenv("EVENT_HUB_SAS_POLICY"),
                'EVENT_HUB_SAS_KEY': os.getenv("EVENT_HUB_SAS_KEY"),
                'OUTPUT_WRITER_PORT': os.getenv("OUTPUT_WRITER_PORT"),
            }
        }
    }

    ow = OutputWriterFactory.create(config)
    assert ow is not None
    assert isinstance(ow.messaging_client, EventHubStreamingClient)
    ow.messaging_client.stop()


@pytest.mark.integration
def test_output_writer_factory_kafka():

    config = {
        'client': {
            'type': 'kafka',
            'config': {
                'KAFKA_TOPIC1': os.getenv("KAFKA_TOPIC"),
                'KAFKA_ADDRESS': os.getenv("KAFKA_ADDRESS"),
                'OUTPUT_WRITER_PORT': os.getenv("OUTPUT_WRITER_PORT"),
            }
        }
    }

    ow = OutputWriterFactory.create(config)
    assert ow is not None
    assert isinstance(ow.messaging_client, KafkaStreamingClient)
    ow.messaging_client.stop()


@pytest.mark.integration
def test_output_writer_flask():

    config = {
        'client': {
            'type': 'kafka',
            'config': {
                'KAFKA_TOPIC': os.getenv("KAFKA_TOPIC"),
                'KAFKA_ADDRESS': os.getenv("KAFKA_ADDRESS"),
                'OUTPUT_WRITER_PORT': os.getenv("OUTPUT_WRITER_PORT"),
                'OUTPUT_WRITER_HOST': os.getenv("OUTPUT_WRITER_HOST"),
            }
        }
    }

    ow = OutputWriterFactory.create(config)
    assert ow is not None
    assert isinstance(ow.listener, FlaskHttpListenerClient)

    received_messages = []

    def receive_callback(message):
        received_messages.append(message)

    ow.listener.start(receive_callback)
