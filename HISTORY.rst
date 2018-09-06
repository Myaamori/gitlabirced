=======
History
=======

0.2.2 (2018-09-06)
------------------

* Improved connection to channels that need registration to join.
* Fixed issue and mr detection on watchers.
* Include more information in logging lines.

0.2.1 (2018-09-03)
------------------

* Small bug fix release. We were missing some dependencies

0.2.0 (2018-09-03)
------------------

* Added watchers support. Now the bot can be hanging
  on a channel giving useful information on MR an Issue
  mentions (e.g. !2, #59).
* Improved support of hook events.
* Improved reconnection of the bot.
* Improve logging, and introudce '-v' option to set the level
  of verbosity (e.g. -vvvv)
* Added authentication options (sasl and NickServ).
* Allow configuring the port used via the configuration file.
* Created plenty of scenario tests using behave.

0.1.3 (2018-08-23)
------------------

* Support added for 'merge_request'

0.1.2 (2018-08-22)
------------------

* First release on PyPI.
* Support added for 'push' and 'issue' events
