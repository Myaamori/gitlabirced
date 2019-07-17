=======
History
=======

0.4.1 (2019-07-17)
------------------

* Added support for Python 3.5. Now this version
  is also tested in the CI.
* Added support for Gitlab Personal Access Tocken in
  the 'watchers' section. Now you can watch private
  projects. Thanks Jonathan!
* Frozen dependencies in the requirements.txt file,
  to avoid random issues like the one fixed in fb99ad91
  (yaml.load vs yaml.safe_load).

0.4.0 (2018-11-11)
------------------

* Added support to ignore WIP merge requests.
* Added support for MR title changes.
* Improved reconnection on initial failure.
* Added support for MR revision changes.
* Improved anti-spam control. If the bot mentions an Issue/MR,
  it will not respond to a watcher command.

0.3.0 (2018-10-20)
------------------

* Added support for update MR assignee hooks.
* Improved reconnection failures.

0.2.3 (2018-10-18)
------------------

* Added support for update issue label hooks.
* Stopped ignoring repeated issue hooks.

0.2.2 (2018-09-06)
------------------

* Improved connection to channels that need registration to join.
* Fixed issue and mr detection on watchers.
* Include more information in logging lines.

0.2.1 (2018-09-03)
------------------

* Small bug fix release. We were missing some dependencies.

0.2.0 (2018-09-03)
------------------

* Added watchers support. Now the bot can be hanging
  on a channel giving useful information on MR an Issue
  mentions (e.g. !2, #59).
* Improved support of hook events.
* Improved reconnection of the bot.
* Improve logging, and introudce '-v' option to set the level
  of verbosity (e.g. -vvvv).
* Added authentication options (sasl and NickServ).
* Allow configuring the port used via the configuration file.
* Created plenty of scenario tests using behave.

0.1.3 (2018-08-23)
------------------

* Support added for 'merge_request'.

0.1.2 (2018-08-22)
------------------

* First release on PyPI.
* Support added for 'push' and 'issue' events.
