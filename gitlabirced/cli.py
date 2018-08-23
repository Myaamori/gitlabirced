# -*- coding: utf-8 -*-

"""Console script for gitlabirced."""
import signal
import sys
import click
import copy
import yaml

from .irc_client import connect_networks
from .http_server import MyHTTPServer, RequestHandler


@click.command()
@click.argument('config-file', nargs=1)
def main(config_file):
    """Console script for gitlabirced."""
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
    all_bots = connect_networks(network_info)

    hooks = config['hooks']
    token = config['token']

    def run_server(addr, port):
        """Start a HTTPServer which waits for requests."""
        httpd = MyHTTPServer(token, hooks, all_bots, (addr, port),
                             RequestHandler)
        httpd.serve_forever()
        print('serving')

    print('going to execute server')
    run_server('0.0.0.0', 1337)

    def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        for b in all_bots:
            all_bots[b]['bot'].reactor.disconnect_all()
            all_bots[b]['process'].terminate()
        click.Abort()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    print('Press Ctrl+C')

    return 0


def _get_channels_per_network(cfg):
    hooks = cfg['hooks']
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
            if ch.startswith('#') and ch not in current_channels:
                print("Appending {channel} ({network})"
                      .format(channel=ch, network=network))
                network_info[network]['channels'].append(ch)
    return network_info


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
