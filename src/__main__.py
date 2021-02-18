#!/usr/bin/env python3
"""Run script.
"""
import logging.config
import os
import shlex
import socket
import sys

import backoff
import httpx
from clinner.command import Type as CommandType
from clinner.command import command
from clinner.run import Main as ClinnerMain

from src.vault import VaultMixin

sys.path.insert(0, os.path.dirname(os.getcwd()))


@backoff.on_exception(backoff.expo, ConnectionError, max_tries=5, logger="cli")
def check_host_alive(host: str, port: str = "80"):
    """Repeatedly try if a port on a host is open.

    :param host: Host IP address or hostname.
    :param port: Port number.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((host, int(port)))
        s.shutdown(socket.SHUT_WR)
    except Exception:
        raise ConnectionError(f'Unavailable host: "{host}"')
    finally:
        s.close()


@command(command_type=CommandType.SHELL, parser_opts={"help": "Run production"})
def start(*args, **kwargs):
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
                "logstash": {"()": "logstash_formatter.LogstashFormatter", "datefmt": "%Y-%m-%dT%H:%M:%S.%f"},
            },
            "handlers": {
                "default": {"level": "DEBUG", "formatter": "standard", "class": "logging.StreamHandler"},
                "mesos": {
                    "level": "INFO",
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "filename": "/srv/apps/mesos/var/sandbox/python.log",
                    "formatter": "logstash",
                    "when": "midnight",
                    "backupCount": 30,
                    "utc": True,
                },
            },
            "loggers": {"src": {"handlers": ["default", "mesos"], "level": "INFO", "propagate": False}},
        }
    )

    return [
        shlex.split(
            f"faust -A src.resources:faust_app worker "
            f"-l info "
            f"-h {os.environ['APP_WEB_HOST']} "
            f"-p {os.environ['APP_WEB_PORT']} "
            f"-b 0.0.0.0"
        )
    ]


@command(command_type=CommandType.SHELL, parser_opts={"help": "Run development"})
def development(*args, **kwargs):
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}},
            "handlers": {"default": {"level": "DEBUG", "formatter": "standard", "class": "logging.StreamHandler"}},
            "loggers": {"src": {"handlers": ["default"], "level": "DEBUG", "propagate": False}},
        }
    )

    return [
        shlex.split("faust -A src.resources:faust_app --debug worker -l info"),
    ]


@command(command_type=CommandType.PYTHON, parser_opts={"help": "Run shell"})
def shell(*args, **kwargs):
    import IPython

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}},
            "handlers": {"default": {"level": "DEBUG", "formatter": "standard", "class": "logging.StreamHandler"}},
            "loggers": {
                "gaps_fix": {"handlers": ["default"], "level": "DEBUG", "propagate": False},
                "nodes": {"handlers": ["default"], "level": "DEBUG", "propagate": False},
            },
        }
    )

    IPython.start_ipython(argv=[])


class Main(VaultMixin, ClinnerMain):
    commands = (
        "clinner.run.commands.black.black",
        "clinner.run.commands.flake8.flake8",
        "clinner.run.commands.isort.isort",
        "clinner.run.commands.pytest.pytest",
        "start",
        "development",
        "shell",
    )

    def inject_app_settings(self):
        """
        Injecting own settings.
        """
        os.environ.setdefault("ENVIRONMENT", self.args.environment)
        os.environ.setdefault("APP_WEB_HOST", "localhost")
        os.environ.setdefault("APP_WEB_PORT", "6066")

    def inject_kafka_url(self):
        """
        Injecting kafka url retrieved from kafka manager.
        """
        if not os.environ.get("KAFKA_URL") and os.environ.get("KAFKA_MANAGER_URL"):
            with httpx.Client() as client:
                try:
                    response = client.get(os.environ["KAFKA_MANAGER_URL"])
                    response.raise_for_status()
                    brokers = response.json()["brokers"]
                    os.environ["KAFKA_URL"] = ";".join([f"kafka://{x['host']}:{x['port']}" for x in brokers])
                except (httpx.HTTPError, KeyError):
                    self.cli.logger.error("Cannot retrieve Kafka brokers")

    def add_arguments(self, parser):
        parser.add_argument("-e", "--environment", help="Environment in which to run the application", default="local")
        parser.add_argument("--check-host", help="Check if a host is alive", action="append", default=[])

    def run(self, *args, **kwargs):
        for host in self.args.check_host:
            check_host_alive(*host.split(":"))

        return super().run(*args, **kwargs)


def main():
    sys.exit(Main().run())


if __name__ == "__main__":
    main()
