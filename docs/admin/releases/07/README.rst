============================================
 ESP Website Stable Release 07 release notes
============================================

.. contents:: :local:

Changelog
=========

New Django version
~~~~~~~~~~~~~~~~~~

We've updated our code to run on Django 1.8, which is the most recent version. This change should be mostly invisible to non-developers. However, it's a major infrastructure change, so if you see any new issues, please let us know. As always, we recommend testing teacher and student registration before opening them, since your site's configuration might be different from what we're testing on.

Improvements to onsite scheduling grid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TODO(lua)

Performance improvements
~~~~~~~~~~~~~~~~~~~~~~~~

This release included several changes which should help improve performance:

- Improved caching on student registration main page

- Improved documentation of program cap, which will improve performance

- Further improvements to the performance of student schedule generation


New scheduling checks
~~~~~~~~~~~~~~~~~~~~~

This release adds three new checks to the scheduling checks module:

- "Hosed teachers", which reports teachers who have registered to teach for at least 2/3 of their available hours. Unlike the other checks on this page, it's intended to be run before scheduling, to give you an idea of who might be tricky to schedule, and will not change as you schedule classes.

- "Classes which are scheduled but aren't approved", which checks for unreviewed, rejected, or cancelled classes that are on the schedule.

- "Classes which are the wrong length or have gaps", which checks for classes where the difference between the start time and end time isn't what it's expected to be.

Sentry integration
~~~~~~~~~~~~~~~~~~

TODO(btidor)

Student schedule extra information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TODO(taylors, lua)

Minor feature additions and bugfixes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Allowed onsite morphed users to bypass required modules

- Fixed grade options on onsite registration form

- Cleaned up or removed a lot of dead code

- Fixed a display issue in custom forms

- Fixed "any flag" filter in class search

- Added resource requests to class search results page

- Added ``created_at`` field to comm panel email models to aid in debugging
  issues

- Removed all usages of "QSD" and "quasi-static data" and replaced with
  "Editable" and "editable text"

- Improvements to dev setup infrastructure

- Miscellaneous fixes and improvements to various scripts

- Fixed a number of typos
