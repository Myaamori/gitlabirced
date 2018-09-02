Feature: Testing watchers functionality

  Scenario: Send a single issue number to channel
     Given gitlabirced running using "data/tests.yaml"
      When client comments "!12" on channel "#ironfoot3"
      Then channel "#ironfoot3" contains "2" messages
       And channel "#ironfoot3" last message is about issue "12"

  Scenario: Send multiple issue numbers to channel
     Given gitlabirced running using "data/tests.yaml"
      When client comments "!13" on channel "#ironfoot3"
      Then channel "#ironfoot3" contains "2" messages
       And channel "#ironfoot3" last message is about issue "13"
      When client comments "!13" on channel "#ironfoot3" "15" times
      Then channel "#ironfoot3" contains "17" messages
       And channel "#ironfoot3" last message is "!13"
      When client comments "!13" on channel "#ironfoot3"
      Then channel "#ironfoot3" contains "19" messages
       And channel "#ironfoot3" last message is about issue "13"

  Scenario: Send a single merge request number to channel
     Given gitlabirced running using "data/tests.yaml"
      When client comments "#22" on channel "#ironfoot3"
      Then channel "#ironfoot3" contains "2" messages
       And channel "#ironfoot3" last message is about merge request "22"

  Scenario: Send multiple merge request numbers to channel
     Given gitlabirced running using "data/tests.yaml"
      When client comments "#23" on channel "#ironfoot3"
      Then channel "#ironfoot3" contains "2" messages
       And channel "#ironfoot3" last message is about merge request "23"
      When client comments "#23" on channel "#ironfoot3" "15" times
      Then channel "#ironfoot3" contains "17" messages
       And channel "#ironfoot3" last message is "#23"
      When client comments "#23" on channel "#ironfoot3"
      Then channel "#ironfoot3" contains "19" messages
       And channel "#ironfoot3" last message is about merge request "23"
