"""
A simpler robserver test server that can serve a specified file over a TCP stream to a connected client.
Run via `python3.6 robserver_tester.py robserver_input/1-in.json`. Logs debug information to stderr.

Used to test robserver prior to the due date and without a reliance on Michael's server implementation.
"""
# pylint: skip-file
import logging
import os
import sys

from Common.json_stream import NetworkJSONStream, StringJSONStream

LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG").upper()
logging.basicConfig(level=LOG_LEVEL)

HOST = "0.0.0.0"
PORT = 1337

with open(sys.argv[1]) as f:
    file_input_reader = StringJSONStream(f.read())

njs = NetworkJSONStream.tcp_server_on(HOST, PORT)

logging.debug(f"Started robserver_tester on {HOST}:{PORT} and established a connection")
name = njs.receive_message()
logging.info(f"Received name={repr(name.assert_value())}")
for chunk_r in file_input_reader.message_iterator():
    njs.send_message(chunk_r.assert_value()).assert_value()
logging.debug("Done sending")
