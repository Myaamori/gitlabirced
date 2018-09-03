Feature: Testing different authentication methods

  Scenario: Send a single push hook
      Given gitlabirced running
      Then network "freenode" channel "NickServ" contains "1" messages
       And network "freenode" log contains "1" messages
       And network "freenode" channel "NickServ" last long message is
           """
           IDENTIFY freenodepass
           """
       And network "freenode" last long log message is
           """
           PRIVMSG NickServ :IDENTIFY freenodepass
           """

      Then network "gimpnet" channel "NickServ" contains "0" messages
       And network "gimpnet" log contains "1" messages
       And network "gimpnet" last long log message is
           """
           PASS gimpnetpass
           """
