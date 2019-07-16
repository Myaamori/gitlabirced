=====
Usage
=====

To use GitlabIRCed in a project::

    import gitlabirced

Command line
------------

Command line usage::

    Usage: gitlabirced [OPTIONS] CONFIG_FILE

    Options:
      -v, --verbose   Verbose mode (-vvv for more, -vvvv max)
      -l, --log TEXT  Log output to this file
      --help          Show this message and exit.

Config file
-----------

An example configuration file: ::

    networks:
      gimp:
        url: irc.gnome.org
        port: 6667
        nick: gitlabirced
        auth: NickServ
        pass: notapassword
      freenode:
        url: irc.freenode.org
        port: 6667
        nick: gitlabirced
        auth: sasl
        pass: notapassword

    hooks:
    - project: palvarez89/definitions
      network: gimp
      reports:
        '##ironfoot': push, merge_request, issue
        'ironfoot': push, merge_request, issue
      branches: master
    - project: palvarez89/definitions
      network: freenode
      reports:
        '##ironfoot': push, merge_request, issue, issue_label, merge_request_assignee, merge_request_update, merge_request_title
        '##ironfoot2': push, merge_request, issue
        'ironfoot': push, merge_request, issue
      branches: master
      wip: yes

    watchers:
    - network: gimp
      channel: '##ironfoot3'
      project: baserock/definitions
      server: http://gitlab.com

    port: 1337
    token: 12345


If you want to use the bot for a private project you can specify a GitLab Personal Access token in the watcher section like so: ::

    watchers:
    - network: gimp
      channel: '##ironfoot3'
      project: baserock/definitions
      server: http://gitlab.com
      gitlabtoken: yourtoken
