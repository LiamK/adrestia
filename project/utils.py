import logging
import sys

class StreamHandlerStdOut(logging.StreamHandler):
    def __init__(self):
        super(StreamHandlerStdOut, self).__init__(sys.stdout)
