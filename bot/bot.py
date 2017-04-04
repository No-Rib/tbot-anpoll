#!/usr/bin/env python

import argparse
import os
import sys

import handler


def main():
    "Main function."

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--token", help="path to Telegram API Token", required=True)

    args = parser.parse_args()

    token = open(args.token, "r").readline()

    bot_handler = handler.Handler(token)


if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        sys.exit("Error: {0}".format(e))
