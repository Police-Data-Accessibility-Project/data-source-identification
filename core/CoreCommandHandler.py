import json
from typing import List, Optional

from collector_manager.CollectorManager import InvalidCollectorError
from collector_manager.collector_mapping import COLLECTOR_MAPPING
from collector_manager.enums import CollectorType
from core.CoreInterface import CoreInterface
from core.SourceCollectorCore import SourceCollectorCore

class InvalidCommandError(Exception):
    pass

class CoreCommandHandler:

    def __init__(self, ci: CoreInterface = CoreInterface()):
        self.ci = ci
        self.commands = {
            "list": self.list_collectors,
            "start": self.start_collector,
            "status": self.get_status,
            "info": self.get_info,
            "close": self.close_collector,
            "exit": self.exit_manager,
        }
        self.running = True
        self.cm = self.core.collector_manager

    def handle_command(self, command: str) -> str:
        parts = command.split()
        if not parts:
            return "Invalid command."

        cmd = parts[0]
        func = self.commands.get(cmd, self.unknown_command)
        try:
            return func(parts)
        except InvalidCommandError as e:
            return str(e)

    def start_collector(self, args: List[str]) -> str:
        collector_name, config = self.parse_args(args)
        try:
            collector_type = CollectorType(collector_name)
        except KeyError:
            raise InvalidCollectorError(f"Collector {collector_name} not found.")
        return self.ci.start_collector(collector_type=collector_type, config=config)

    def get_cid(self, cid_str: str) -> int:
        try:
            return int(cid_str)
        except ValueError:
            raise InvalidCommandError(f"CID must be an integer")

    def parse_args(self, args: List[str]) -> (Optional[str], Optional[dict]):
        if len(args) < 2:
            raise InvalidCommandError("Usage: start {collector_name}")

        collector_name = args[1]
        config = None

        if len(args) > 3 and args[2] == "--config":
            config = self.load_config(args[3])

        return collector_name, config

    def load_config(self, file_path: str) -> Optional[dict]:
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise InvalidCommandError(f"Config file not found: {file_path}")
        except json.JSONDecodeError:
            raise InvalidCommandError(f"Invalid config file: {file_path}")

    def exit_manager(self, args: List[str]):
        self.running = False
        return "Exiting Core Manager."

    def unknown_command(self, args: List[str]):
        return "Unknown command."

    def close_collector(self, args: List[str]):
        if len(args) < 2:
            return "Usage: close {cid}"
        cid = self.get_cid(cid_str=args[1])
        try:
            lifecycle_info = self.cm.close_collector(cid)
            return lifecycle_info.message
        except InvalidCollectorError:
            return f"Collector {cid} not found."
        return self.ci.close_collector(cid=cid)

    def get_info(self, args: List[str]):
        if len(args) < 2:
            return "Usage: info {cid}"
        cid = self.get_cid(cid_str=args[1])
        return self.ci.get_info(cid)

    def get_status(self, args: List[str]):
        if len(args) > 1:
            cid = self.get_cid(args[1])
            return self.ci.get_status(cid)
        else:
            return self.ci.get_status()

    def list_collectors(self, args: List[str]):
        return self.ci.list_collectors()
