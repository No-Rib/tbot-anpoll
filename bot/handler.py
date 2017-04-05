"""Provides Handler class."""

from functools import wraps

import telepot

from utils import decorator

_ACTION_LIST_RESPONDENTS = "/list-respondents"
_ACTION_START = "/start"
_ACTION_STOP = "/stop"
"""Supported actons."""

_STATE_STARTED = "started"
_STATE_STOPPED = "stopped"
"""Possible Handler states."""


class BotError(Exception):
    def __init__(self, msg):
        super(BotError, self).__init__(self, msg)


class BotNotInitialized(BotError):
    def __init__(self, msg="Bot is not initialized."):
        super(BotNotInitialized, self).__init__(self, msg)


class BotAPIError(BotError):
    def __init__(self, msg, botmsg=None):
        super(BotAPIError, self).__init__(self, msg)

        self.botmsg = botmsg if botmsg else msg


class InvalidHandlerState(BotAPIError):
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
        self.respondents = set()
        self.state = _STATE_STOPPED
        self.token = token

    def _run_when_initialized(func):
        """Raises exception if action is run with bot not being initialized."""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.bot:
                raise BotNotInitialized()
            else:
                return func(self, *args, **kwargs)
        return wrapper

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

    @_run_when_initialized
    def send_message(self, chat_id, msg):
        """Sends message to specific chat."""

        self.bot.sendMessage(chat_id, msg)

    def handler(self, msg):
        """Tbot message handler."""

        body = msg["text"]
        chat_id = msg["chat"]["id"]

        try:
            if body == _ACTION_START:
                self.handle_start_action(chat_id)
            elif body == _ACTION_STOP:
                self.handle_stop_action(chat_id)
        except BotAPIError as e:
            self.bot.sendMessage(chat_id, e.botmsg)
            raise e
        except Exception as e:
            raise e

    @_run_when_in_state(_STATE_STOPPED)
    @_run_when_initialized
    def handle_start_action(self, chat_id)
        """Handles '/start' action """

        self.state = _STATE_STARTED
        self.send_message(chat_id, "Handler has been started.")
        print "Handler has been started."

    @_run_when_in_state(_STATE_STARTED)
    def handle_stop_action(self, chat_id):
        """Handles '/stop' action """

        self.state = _STATE_STOPPED
        self.send_message(chat_id, "Handler has been stopped.")
        print "Handler has been stopped."

    def run(self):
        """Initializes handler loop."""

        self.bot = telepot.Bot(self.token)
        self.loop = self.bot.message_loop(self.handler, run_forever="Running")
