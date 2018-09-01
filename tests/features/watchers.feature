Feature: Testing watchers functionality

  Scenario: Send a single issue number to channel
     Given gitlabirced running using "data/tests.yaml"
      When client comments "!12" on channel "#ironfoot3"
      Then channel "#ironfoot3" contains "2" messages
       And channel "#ironfoot3" last message is about issue "12"

  Scenario: Send a multiple issue number to channel
     Given gitlabirced running using "data/tests.yaml"
      When client comments "!12" on channel "#ironfoot3"
      Then channel "#ironfoot3" contains "2" messages
       And channel "#ironfoot3" last message is about issue "12"
      When client comments "!12" on channel "#ironfoot3" "15" times
      Then channel "#ironfoot3" contains "17" messages
       And channel "#ironfoot3" last message is "!12"
      When client comments "!12" on channel "#ironfoot3"
      Then channel "#ironfoot3" contains "19" messages
       And channel "#ironfoot3" last message is about issue "12"
