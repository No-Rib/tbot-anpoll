#!/usr/bin/env python

import argparse
import sys

import handler


def main():
    "Main function."

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--token", help="path to Telegram API Token", required=True)
    parser.add_argument(
        "--admins", help="path to list of admin users", required=True)

    args = parser.parse_args()

    token = open(args.token, "r").readline().strip()

    admins = []
    if args.admins:
        with open(args.admins, "r") as f:
            admins = [line.strip() for line in f]

    if not admins:
        raise Exception("Admins list should not be empty.")

    bot_handler = handler.Handler(token, admins)
    bot_handler.run()

if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        sys.exit("Error: {0}".format(e))
