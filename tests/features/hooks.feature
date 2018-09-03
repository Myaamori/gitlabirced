Feature: Testing watchers functionality

  Scenario: Send a single push hook
     Given a gitlabirced hook
        | key       | value        |
        | project   | pa/dn        |
        | network   | gimpnet      |
        | report    | #chan1: push |
        | report    | #chan2: push |
        | branches  | master       |
       And gitlabirced running
      When a push hook about project "pa/dn" branch "master" is received
      Then network "gimpnet" channel "#chan1" contains "1" messages
       And network "gimpnet" channel "#chan1" last long message is
           """
           jsmith pushed on Pa Dn@master: 4 commits (last: fixed readme)
           """

      Then network "gimpnet" channel "#chan2" contains "1" messages
       And network "gimpnet" channel "#chan2" last long message is
           """
           jsmith pushed on Pa Dn@master: 4 commits (last: fixed readme)
           """
      When a push hook about project "pa/dn" branch "another" is received
      Then network "gimpnet" channel "#chan1" contains "1" messages
       And network "gimpnet" channel "#chan2" contains "1" messages

  Scenario: Send a single issue hook
     Given a gitlabirced hook
        | key       | value         |
        | project   | pa/example    |
        | network   | freenode      |
        | report    | #chan3: issue |
        | report    | #chan4: issue |
       And gitlabirced running
      When an issue "open" hook about project "pa/example" is received
      Then network "freenode" channel "#chan3" contains "1" messages
       And network "freenode" channel "#chan3" last long message is
           """
           root opened issue #23 (New API: create/update/delete file) on Pa Example http://example.com/diaspora/issues/23
           """

      Then network "freenode" channel "#chan4" contains "1" messages
       And network "freenode" channel "#chan4" last long message is
           """
           root opened issue #23 (New API: create/update/delete file) on Pa Example http://example.com/diaspora/issues/23
           """

      When an issue "open" hook about project "pa/example" is received
      Then network "freenode" channel "#chan3" contains "1" messages
       And network "freenode" channel "#chan4" contains "1" messages

      When an issue "close" hook about project "pa/example" is received
      Then network "freenode" channel "#chan3" contains "2" messages
       And network "freenode" channel "#chan3" last long message is
           """
           root closed issue #23 (New API: create/update/delete file) on Pa Example http://example.com/diaspora/issues/23
           """
      Then network "freenode" channel "#chan4" contains "2" messages
       And network "freenode" channel "#chan4" last long message is
           """
           root closed issue #23 (New API: create/update/delete file) on Pa Example http://example.com/diaspora/issues/23
           """

  Scenario: Send a single merge request hook
     Given a gitlabirced hook
        | key       | value                 |
        | project   | pa/another            |
        | network   | freenode              |
        | report    | #chan5: merge_request |
        | report    | #chan6: merge_request |
       And gitlabirced running
      When a merge request "open" hook about project "pa/another" is received
      Then network "freenode" channel "#chan5" contains "1" messages
       And network "freenode" channel "#chan5" last long message is
           """
           root opened MR !1 (ms-viewport->master: MS-Viewport) on Pa Another http://example.com/diaspora/merge_requests/1
           """

      Then network "freenode" channel "#chan6" contains "1" messages
       And network "freenode" channel "#chan6" last long message is
           """
           root opened MR !1 (ms-viewport->master: MS-Viewport) on Pa Another http://example.com/diaspora/merge_requests/1
           """

      When a merge request "update" hook about project "pa/another" is received
      Then network "freenode" channel "#chan5" contains "1" messages
       And network "freenode" channel "#chan6" contains "1" messages

      When a merge request "close" hook about project "pa/another" is received
      Then network "freenode" channel "#chan5" contains "2" messages
       And network "freenode" channel "#chan5" last long message is
           """
           root closed MR !1 (ms-viewport->master: MS-Viewport) on Pa Another http://example.com/diaspora/merge_requests/1
           """

      Then network "freenode" channel "#chan6" contains "2" messages
       And network "freenode" channel "#chan6" last long message is
           """
           root closed MR !1 (ms-viewport->master: MS-Viewport) on Pa Another http://example.com/diaspora/merge_requests/1
           """
