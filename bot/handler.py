"""Provides Handler class."""

import telepot


class Handler(object):
    """AnPoll Tbot handler class."""

    def __init__(self, token, admins=None):

        self.admins = admins or []
        self.bot = None
        self.loop = None
        self.state = None
        self.token = token
