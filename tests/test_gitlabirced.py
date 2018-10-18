#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `gitlabirced` package."""

import pytest

from click.testing import CliRunner

from gitlabirced import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface_no_args():
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 2
    assert 'Error: Missing argument "CONFIG_FILE"' in result.output


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    # result = runner.invoke(cli.main, ['tests/conf.yaml'])
    # assert result.exit_code == 0
    # assert 'gitlabirced.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help          Show this message and exit.' in help_result.output
    assert '-l, --log TEXT  Log output to this file' in help_result.output
    assert ('-v, --verbose   Verbose mode (-vvv for more, -vvvv max)'
            in help_result.output)
