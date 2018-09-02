Feature: Testing watchers functionality

  Scenario: Send a single issue number to channel
     Given a gitlabirced watcher
        | key       | value                 |
        | network   | freenode              |
        | channel   | #channel1             |
        | project   | baserock/definitions  |
       And gitlabirced running
      When client comments "!12" on "freenode" channel "#channel1"
      Then network "freenode" channel "#channel1" contains "2" messages
       And network "freenode" channel "#channel1" last message is about issue "12"

  Scenario: Send multiple issue numbers to channel
     Given a gitlabirced watcher
        | key       | value                 |
        | network   | freenode              |
        | channel   | #channel2             |
        | project   | baserock/definitions  |
       And gitlabirced running
      When client comments "!13" on "freenode" channel "#channel2"
      Then network "freenode" channel "#channel2" contains "2" messages
       And network "freenode" channel "#channel2" last message is about issue "13"
      When client comments "!13" on "freenode" channel "#channel2" "15" times
      Then network "freenode" channel "#channel2" contains "17" messages
       And network "freenode" channel "#channel2" last message is "!13"
      When client comments "!13" on "freenode" channel "#channel2"
      Then network "freenode" channel "#channel2" contains "19" messages
       And network "freenode" channel "#channel2" last message is about issue "13"

  Scenario: Send a single merge request number to channel
     Given a gitlabirced watcher
        | key       | value                 |
        | network   | gimpnet               |
        | channel   | #channel3             |
        | project   | baserock/definitions  |
       And gitlabirced running
      When client comments "#22" on "gimpnet" channel "#channel3"
      Then network "gimpnet" channel "#channel3" contains "2" messages
       And network "gimpnet" channel "#channel3" last message is about merge request "22"

  Scenario: Send multiple merge request numbers to channel
     Given a gitlabirced watcher
        | key       | value                 |
        | network   | gimpnet               |
        | channel   | #channel4             |
        | project   | baserock/definitions  |
       And gitlabirced running
      When client comments "#23" on "gimpnet" channel "#channel4"
      Then network "gimpnet" channel "#channel4" contains "2" messages
       And network "gimpnet" channel "#channel4" last message is about merge request "23"
      When client comments "#23" on "gimpnet" channel "#channel4" "15" times
      Then network "gimpnet" channel "#channel4" contains "17" messages
       And network "gimpnet" channel "#channel4" last message is "#23"
      When client comments "#23" on "gimpnet" channel "#channel4"
      Then network "gimpnet" channel "#channel4" contains "19" messages
       And network "gimpnet" channel "#channel4" last message is about merge request "23"
