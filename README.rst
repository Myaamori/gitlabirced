===========
GitlabIRCed
===========


.. image:: https://img.shields.io/pypi/v/gitlabirced.svg
        :target: https://pypi.python.org/pypi/gitlabirced

.. image:: https://gitlab.com/palvarez89/gitlabirced/badges/master/pipeline.svg
        :target: https://gitlab.com/palvarez89/gitlabirced/commits/master

.. image:: https://gitlab.com/palvarez89/gitlabirced/badges/master/coverage.svg?job=tests
        :target: https://gitlab.com/palvarez89/gitlabirced/commits/master

.. image:: https://readthedocs.org/projects/gitlabirced/badge/?version=latest
        :target: https://gitlabirced.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


IRC bot that connects with your GitLab projects


* Free software: MIT license
* Documentation: https://gitlabirced.readthedocs.io.


Features
--------

**GitlabIRCed** bot will let you connect your Gitlab projects with their IRC channels. There are main functions of this bot:

* **Hooks**: The bot will receive web hooks sent by Gitlab on different events.
  You can configure the bot to stream these events into one or many IRC channels
  and networks.
* **Watchers**: The bot can be configured to link an IRC channel to a project. The bot
  will watch the messages and give extra information when a MR or an Issue is mentioned.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
