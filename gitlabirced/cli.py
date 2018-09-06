# -*- coding: utf-8 -*-

"""Console script for gitlabirced."""
import click
import copy
import logging
import signal
import sys
import threading
import yaml

from irc.client import is_channel

from .irc_client import connect_networks
from .http_server import MyHTTPServer, RequestHandler

cli_logger = logging.getLogger(__name__)


@click.command()
@click.argument('config-file', nargs=1)
@click.option('-v', '--verbose', count=True,
              help="Verbose mode (-vvv for more, -vvvv max)")
@click.option('-l', '--log', help="Log output to this file")
def main(config_file, verbose, log):
    _configure_logging(verbose, log)
    config = load_config(config_file)
    print(config)
    client = Client(config)
    client.start()
    signal.signal(signal.SIGINT, client.stop)


def load_config(config_file):
    try:
        with open(config_file, 'r') as stream:
            config = yaml.load(stream)
            print("Configuration loaded %s" % config)
    except yaml.YAMLError as exc:
        print(exc)
        sys.exit(1)
    except IOError:
        print("File %s not found" % config_file)
        sys.exit(3)
    return config


class Client():
    def __init__(self, config):
        self.config = config
        self.all_bots = []

    def stop(self, sig=None, frame=None):
        print('You pressed Ctrl+C!')
        for b in self.all_bots:
            self.all_bots[b]['bot'].shutdown()
        self.httpd.shutdown()

    def start(self):
        """Console script for gitlabirced."""

        network_info = _get_channels_per_network(self.config)
        watchers = self.config.get('watchers')
        print('going to connect networks')
        self.all_bots = connect_networks(network_info, watchers)

        hooks = self.config.get('hooks', {})
        token = self.config['token']

        def run_server(addr, port):
            """Start a HTTPServer which waits for requests."""
            self.httpd = MyHTTPServer(token, hooks, self.all_bots,
                                      (addr, port), RequestHandler)
            thread = threading.Thread(target=self.httpd.serve_forever)
            thread.start()
            _, self.port_used = self.httpd.socket.getsockname()

        print('going to execute server')
        port = self.config.get('port', 0)
        if port == 0:
            cli_logger.warning('WARNING: Port not specified in the '
                               'configuration. A random one will be used')
        run_server('0.0.0.0', port)
        if port == 0:
            cli_logger.warning('WARNING: Port used {port}'
                               .format(port=self.port_used))
        print('Press Ctrl+C')

        return 0


def _get_channels_per_network(cfg):
    hooks = cfg.get('hooks', {})
    network_info = copy.deepcopy(cfg['networks'])
    for net_key in network_info:
        network_info[net_key]['channels'] = []

    for hook in hooks:
        network = hook['network']
        if network not in network_info:
            raise Exception("Network '{network}' not configured"
                            .format(network=network))

        reports = hook['reports']
        for ch in reports:
            current_channels = network_info[network]['channels']
            if is_channel(ch) and ch not in current_channels:
                print("Appending {channel} ({network})"
                      .format(channel=ch, network=network))
                network_info[network]['channels'].append(ch)

    watchers = cfg.get('watchers', {})
    print(watchers)
    for watcher in watchers:
        network = watcher['network']
        channel = watcher['channel']
        current_channels = network_info[network]['channels']
        if channel not in current_channels:
            print("Appending {channel} ({network})"
                  .format(channel=channel, network=network))
            network_info[network]['channels'].append(channel)

    return network_info


def _configure_logging(verbosity, output_file=None):
    """ Configures logging level in different ways.

    :param verbosity: The verbosity level (0-4)
      0: logging.WARNING
      1: logging.INFO
      2: logging.DEBUG
      3: (root) logging.INFO
      4: (root) logging.DEBUG
    :param output_file: If set, file to put the logs.
    """
    our_module_name = __name__.split('.')[0]
    our_logger = logging.getLogger(our_module_name)
    root_logger = logging.getLogger()

    our_level = None
    root_level = None

    if verbosity == 1:
        our_level = logging.INFO
    elif verbosity == 2:
        our_level = logging.DEBUG
    if verbosity == 3:
        root_level = logging.INFO
    if verbosity >= 4:
        root_level = logging.DEBUG

    if root_level:
        root_logger.setLevel(root_level)
    elif our_level:
        our_logger.setLevel(our_level)

    if output_file:
        handler = logging.FileHandler(output_file)
    else:
        handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
