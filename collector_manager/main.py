"""
This starts up the collector manager Command Line Interface (CLI)
"""

from collector_manager.CollectorManager import CollectorManager
from collector_manager.CommandHandler import CommandHandler


def main():
    cm = CollectorManager()
    handler = CommandHandler(cm)
    print("Collector Manager CLI")
    while handler.running:
        command = input("Enter command: ")
        handler.handle_command(command)


if __name__ == "__main__":
    main()
