"""Provides Handler class."""

from functools import wraps

import telepot

from utils import decorator


class InvalidHandlerState(Exception):
    def __init__(self, state):
        super(InvalidHandlerState, self).__init__(
            "This action should be run in '{0}' state".format(state)
        )


class Handler(object):
    """AnPoll Tbot handler class."""

    _ACTION_START = "start"
    _ACTION_STOP = "stop"
    """Supported actons."""

    _STATE_STARTED = "started"
    _STATE_STOPPED = "stopped"
    """Possible Handler states."""

    def __init__(self, token, admins=None):

        self.admins = admins or []
        self.bot = None
        self.loop = None
        self.state = self._STATE_STOPPED
        self.token = token

    @decorator
    def _run_when_in_state(self, state):
        @wraps
        def outer(func):
            @wraps
            def inner(*args, **kwargs):
                if self.state != state:
                    raise InvalidHandlerState(state)
                else:
                    return func(*args, **kwargs)
            return inner
        return outer

    def handler(self, msg):
        """Tbot message handler."""

        pass

    def run(self):
        """Initializes handler loop."""

        self.bot = telepot.Bot(self.token)
        self.loop = self.bot.message_loop(self.handler, run_forever="Running")
