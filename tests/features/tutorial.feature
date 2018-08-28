Feature: Testing watchers functionality

  Scenario: Send a single issue number to channel
     Given gitlabirced running using "data/tests.yaml"
      When client comments "!12" on channel "#ironfoot3"
       And we give some time to the bot
      Then channel "#ironfoot3" contains "2" messages
       And channel "#ironfoot3" last message is about issue "12"
