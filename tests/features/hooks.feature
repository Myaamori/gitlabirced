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

  Scenario: Send a single issue label update hook
     Given a gitlabirced hook
        | key       | value               |
        | project   | pa/example_label    |
        | network   | freenode            |
        | report    | #chan7: issue_label |
        | report    | #chan8: issue_label |
       And gitlabirced running
      When an issue update "label" hook about project "pa/example_label" is received
      Then network "freenode" channel "#chan7" contains "1" messages
       And network "freenode" channel "#chan7" last long message is
           """
           toscalix added 'Important', 'To Do' label(s) to issue #650 (RFE: Add plugin to generate snaps) on Pa Example_Label https://gitlab.com/BuildStream/buildstream/issues/650
           """

      Then network "freenode" channel "#chan8" contains "1" messages
       And network "freenode" channel "#chan8" last long message is
           """
           toscalix added 'Important', 'To Do' label(s) to issue #650 (RFE: Add plugin to generate snaps) on Pa Example_Label https://gitlab.com/BuildStream/buildstream/issues/650
           """

  Scenario: Send a single MR assignee update hook
     Given a gitlabirced hook
        | key       | value                           |
        | project   | pa/example_assignee             |
        | network   | freenode                        |
        | report    | #chan9: merge_request_assignee  |
        | report    | #chan10: merge_request_assignee |
       And gitlabirced running
      When a merge request update "assignee" hook about project "pa/example_assignee" is received
      Then network "freenode" channel "#chan9" contains "1" messages
       And network "freenode" channel "#chan9" last long message is
           """
           fsdk-marge-bot assigned valentindavid to MR !575 (valentindavid/rpath->18.08: Fix useles RPATH generated by libtool) on Pa Example_Assignee https://gitlab.com/palvarez89/definitions/merge_requests/575
           """

      Then network "freenode" channel "#chan10" contains "1" messages
       And network "freenode" channel "#chan10" last long message is
           """
           fsdk-marge-bot assigned valentindavid to MR !575 (valentindavid/rpath->18.08: Fix useles RPATH generated by libtool) on Pa Example_Assignee https://gitlab.com/palvarez89/definitions/merge_requests/575
           """
