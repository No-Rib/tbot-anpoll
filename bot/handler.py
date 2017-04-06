"""Provides Handler class."""

from functools import wraps
import re

import telepot

_ACTION_LIST_ADMINS = "/list_admins"
_ACTION_LIST_RESPONDENTS = "/list_respondents"
_ACTION_ADD_ADMINS = "/add_admins"
_ACTION_ADD_RESPONDENTS = "/add_respondents"
_ACTION_START = "/start"
_ACTION_STOP = "/stop"
"""Supported actons."""

_ACTION_REGEX = re.compile("^/\w+")
"""Valid action pattern."""


def _is_action(text):
    """Checks if text given is Telegram bot action"""
    return bool(_ACTION_REGEX.match(text))


_STATE_STARTED = "started"
_STATE_STOPPED = "stopped"
"""Possible Handler states."""

_USERNAME_REGEX = re.compile("^@[a-z0-9_]{5,}$")
"""Valid Telegram username pattern."""


def _is_username(username):
    """Checks if given string is valid Telegram username."""
    # TODO Make check more elaborate?
    return bool(_USERNAME_REGEX.match(username))


class BotError(Exception):
    def __init__(self, msg):
        super(BotError, self).__init__(msg)


class BotNotInitialized(BotError):
    def __init__(self, msg="Bot is not initialized."):
        super(BotNotInitialized, self).__init__(msg)


class BotAPIError(BotError):
    def __init__(self, msg, botmsg=None):
        super(BotAPIError, self).__init__(msg)

        self.botmsg = botmsg if botmsg else msg


class InvalidHandlerState(BotAPIError):
    def __init__(self, state):
        super(InvalidHandlerState, self).__init__(
            "This action should be run in '{0}' state".format(state)
        )


class ExistingLock(BotAPIError):
    def __init__(self, action):
        super(ExistingLock, self).__init__(
            "Cannot perform the action. '{0}'' is expecting input.".format(
                action)
        )


class InvalidUsername(BotAPIError):
    def __init__(self, username):
        super(InvalidUsername, self).__init__(
            "Username '{0}' is invalid.".format(username)
        )


class UnknownAction(BotAPIError):
    def __init__(self):
        super(UnknownAction, self).__init__("Unknown action.")


def _format_name_list(names):
    """Returns formatted for printing list of names."""
    return "\n".join(sorted(names)) if names else "Empty!"


def _tokenize_usernames(payload):
    """Transforms string with usernames to set of usernames."""

    usernames = payload.split("\n")
    for username in usernames:
        if not _is_username(username):
            raise InvalidUsername(username)
    return set(usernames)


class Handler(object):
    """AnPoll Tbot handler class."""

    def __init__(self, token, admins=None):

        self.admins = set(admins or [])
        self.bot = None
        self.locks = {}
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

    def _lock_user(func):
        """Adds lock for user."""
        @wraps(func)
        def wrapper(self, chat_id, msg, *args, **kwargs):
            username = msg["chat"]["username"]
            action = msg["text"]
            if username in self.locks:
                raise ExistingLock(self.locks.get(username))
            else:
                self.locks[username] = action
            return func(self, chat_id, msg, *args, **kwargs)
        return wrapper

    def _unlock_user(func):
        """Removes lock if func run was successful."""
        @wraps(func)
        def wrapper(self, chat_id, msg, *args, **kwargs):
            result = func(self, chat_id, msg, *args, **kwargs)
            self.locks.pop(msg["chat"]["username"], None)
            return result
        return wrapper

    @_run_when_initialized
    def send_message(self, chat_id, msg):
        """Sends message to specific chat."""

        self.bot.sendMessage(chat_id, msg)

    def handler(self, msg):
        """Tbot message handler."""

        body = msg["text"]
        chat_id = msg["chat"]["id"]
        username = msg["chat"]["username"]

        try:
            if _is_action(body):
                if body == _ACTION_START:
                    self.handle_start_action(chat_id)
                elif body == _ACTION_STOP:
                    self.handle_stop_action(chat_id, msg)
                elif body == _ACTION_LIST_ADMINS:
                    self.handle_list_admins(chat_id)
                elif body == _ACTION_LIST_RESPONDENTS:
                    self.handle_list_respondents(chat_id)
                elif body == _ACTION_ADD_ADMINS:
                    self.handle_add_admins(chat_id, msg)
                elif body == _ACTION_ADD_RESPONDENTS:
                    self.handle_add_respondents(chat_id, msg)
                else:
                    raise UnknownAction()
            else:
                lock = self.locks.get(username)
                if lock:
                    if lock == _ACTION_ADD_ADMINS:
                        self.commit_add_admins(chat_id, msg)
                    if lock == _ACTION_ADD_RESPONDENTS:
                        self.commit_add_respondents(chat_id, msg)
        except BotAPIError as e:
            self.bot.sendMessage(chat_id, e.botmsg)
            raise e
        except Exception as e:
            raise e

    @_run_when_in_state(_STATE_STOPPED)
    @_run_when_initialized
    def handle_start_action(self, chat_id):
        """Handles '/start' action."""

        self.state = _STATE_STARTED
        self.send_message(chat_id, "Handler has been started.")
        print "Handler has been started."

    @_unlock_user
    @_run_when_in_state(_STATE_STARTED)
    @_run_when_initialized
    def handle_stop_action(self, chat_id, msg):
        """Handles '/stop' action """

        self.state = _STATE_STOPPED
        self.send_message(chat_id, "Handler has been stopped.")
        print "Handler has been stopped."

    @_run_when_in_state(_STATE_STARTED)
    @_run_when_initialized
    def handle_list_admins(self, chat_id):
        """Handles 'list_admins' action."""

        self.send_message(chat_id, _format_name_list(self.admins))

    @_run_when_in_state(_STATE_STARTED)
    @_run_when_initialized
    def handle_list_respondents(self, chat_id):
        """Handles 'list_respondents' action."""

        self.send_message(chat_id, _format_name_list(self.respondents))

    @_lock_user
    @_run_when_in_state(_STATE_STARTED)
    @_run_when_initialized
    def handle_add_admins(self, chat_id, msg):
        """Handles 'add_admins' action."""

        self.send_message(chat_id, "Enter list of admins (one per line):")

    @_unlock_user
    @_run_when_in_state(_STATE_STARTED)
    @_run_when_initialized
    def commit_add_admins(self, chat_id, msg):
        """Commits 'add_admins' payload."""

        admins = _tokenize_usernames(msg["text"])
        self.admins.update(admins)

    @_lock_user
    @_run_when_in_state(_STATE_STARTED)
    @_run_when_initialized
    def handle_add_respondents(self, chat_id, msg):
        """Handles 'add_respondents' action."""

        self.send_message(chat_id, "Enter list of respondents (one per line):")

    @_unlock_user
    @_run_when_in_state(_STATE_STARTED)
    @_run_when_initialized
    def commit_add_respondents(self, chat_id, msg):
        """Commits 'add_respondents' payload."""

        respondents = _tokenize_usernames(msg["text"])
        self.respondents.update(respondents)

    def run(self):
        """Initializes handler loop."""

        self.bot = telepot.Bot(self.token)
        self.loop = self.bot.message_loop(self.handler, run_forever="Running")
