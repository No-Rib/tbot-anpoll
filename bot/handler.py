"""Provides Handler class."""

from functools import wraps

import telepot

from utils import decorator

_ACTION_START = "/start"
_ACTION_STOP = "/stop"
"""Supported actons."""

_STATE_STARTED = "started"
_STATE_STOPPED = "stopped"
"""Possible Handler states."""


class BotError(Exception):
    def __init__(self, msg, botmsg=None):
        super(BotError, self).__init__(self, msg)

        self.botmsg = botmsg if botmsg else msg


class InvalidHandlerState(BotError):
    def __init__(self, state):
        super(InvalidHandlerState, self).__init__(
            "This action should be run in '{0}' state".format(state)
        )


class Handler(object):
    """AnPoll Tbot handler class."""

    def __init__(self, token, admins=None):

        self.admins = admins or []
        self.bot = None
        self.loop = None
        self.state = _STATE_STOPPED
        self.token = token

    def _run_when_in_state(state):
        def outer(func):
            @wraps(func)
            def inner(self, *args, **kwargs):
                if self.state != state:
                    raise InvalidHandlerState(state)
                else:
                    return func(self, *args, **kwargs)
            return inner
        return outer

    def handler(self, msg):
        """Tbot message handler."""

        body = msg["text"]
        chat_id = msg["chat"]["id"]

        try:
            if body == _ACTION_START:
                self.handle_start_action()
            elif body == _ACTION_STOP:
                self.handle_stop_action()
        except BotError as e:
            self.bot.sendMessage(chat_id, e.botmsg)
            raise e
        except Exception as e:
            raise e

    @_run_when_in_state(_STATE_STOPPED)
    def handle_start_action(self):
        """Handles '/start' action """

        self.state = _STATE_STARTED
        print "Handler has been started."

    @_run_when_in_state(_STATE_STARTED)
    def handle_stop_action(self):
        """Handles '/stop' action """

        self.state = _STATE_STOPPED
        print "Handler has been stopped."

    def run(self):
        """Initializes handler loop."""

        self.bot = telepot.Bot(self.token)
        self.loop = self.bot.message_loop(self.handler, run_forever="Running")
