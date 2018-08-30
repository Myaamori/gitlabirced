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


@click.command()
@click.argument('config-file', nargs=1)
@click.option('-v', '--verbose', count=True)
def main(config_file, verbose):
    client = Client(config_file, verbose)
    client.start()
    signal.signal(signal.SIGINT, client.stop)


class Client():
    def __init__(self, config_file, verbose):
        self.config_file = config_file
        self.verbose = verbose
        self.all_bots = []

    def stop(self, sig=None, frame=None):
        print('You pressed Ctrl+C!')
        for b in self.all_bots:
            self.all_bots[b]['bot'].shutdown()
        self.httpd.shutdown()

    def start(self):
        """Console script for gitlabirced."""
        verbose = self.verbose
        config_file = self.config_file

        _configure_logging(verbose)
        click.echo(config_file)

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

        network_info = _get_channels_per_network(config)
        watchers = config.get('watchers')
        print('going to connect networks')
        self.all_bots = connect_networks(network_info, watchers)

        hooks = config['hooks']
        token = config['token']

        def run_server(addr, port):
            """Start a HTTPServer which waits for requests."""
            self.httpd = MyHTTPServer(token, hooks, self.all_bots,
                                      (addr, port), RequestHandler)
            thread = threading.Thread(target=self.httpd.serve_forever)
            thread.start()

        print('going to execute server')
        # TODO: move these 2 values to the configuration file
        run_server('0.0.0.0', 1337)
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


def _configure_logging(verbosity):
    """ Configures logging level in different ways.

    :param verbosity: The verbosity level (0-4)
      0: logging.WARNING
      1: logging.INFO
      2: logging.DEBUG
      3: (root) logging.INFO
      4: (root) logging.DEBUG
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

    root_logger.addHandler(logging.StreamHandler())


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
