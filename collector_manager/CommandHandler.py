"""
Command Handler

This module provides a command handler for the Collector Manager CLI.
"""
import json
from typing import List

from collector_manager.CollectorManager import CollectorManager, InvalidCollectorError


class CommandHandler:
    def __init__(self, cm: CollectorManager):
        self.cm = cm
        self.commands = {
            "list": self.list_collectors,
            "start": self.start_collector,
            "status": self.get_status,
            "info": self.get_info,
            "close": self.close_collector,
            "exit": self.exit_manager,
        }
        self.running = True

    def handle_command(self, command: str):
        parts = command.split()
        if not parts:
            return

        cmd = parts[0]
        func = self.commands.get(cmd, self.unknown_command)
        func(parts)

    def list_collectors(self, args: List[str]):
        print(" " + "\n ".join(self.cm.list_collectors()))

    def start_collector(self, args: List[str]):
        if len(args) < 2:
            print("Usage: start {collector_name}")
            return
        collector_name = args[1]
        config = None
        # TODO: Refactor and extract functions
        if len(args) > 3 and args[2] == "--config":
            try:
                f = open(args[3], "r")
            except FileNotFoundError:
                print(f"Config file not found: {args[3]}")
                return
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                print(f"Invalid config file: {args[3]}")
        try:
            cid = self.cm.start_collector(collector_name, config)
        except InvalidCollectorError:
            print(f"Invalid collector name: {collector_name}")
            return
        print(f"Started collector with CID: {cid}")

    def get_status(self, args: List[str]):
        if len(args) > 1:
            cid = args[1]
            print(self.cm.get_status(cid))
        else:
            print("\n".join(self.cm.get_status()))

    def get_info(self, args: List[str]):
        if len(args) < 2:
            print("Usage: info {cid}")
            return
        cid = args[1]
        print(self.cm.get_info(cid))

    def close_collector(self, args: List[str]):
        if len(args) < 2:
            print("Usage: close {cid}")
            return
        cid = args[1]
        print(self.cm.close_collector(cid))

    def exit_manager(self, args: List[str]):
        print("Exiting Collector Manager.")
        self.running = False

    def unknown_command(self, args: List[str]):
        print("Unknown command.")
