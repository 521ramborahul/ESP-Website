============================================
 ESP Website Stable Release 06 release notes
============================================

.. contents:: :local:

Changelog
=========

Improvements to scheduling checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The "Scheduling Diagnostics" module has undergone significant improvements.
Now, instead of waiting a long time for all the checks to be run and rendered,
the page loads instantaneously, and you can run and see the results of
whichever individual checks you want.

If the "Scheduling Diagnostics" module is enabled for the program, you can get
to the scheduling checks page by clicking the link "Run Scheduling Diagnostics"
(/manage/[program]/[instance]/scheduling_checks) on the main program
management.

Class flags improvements
~~~~~~~~~~~~~~~~~~~~~~~~

Lottery Student Registration Big Board
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Logging current grade during student grade change request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tags to disable shirt types question in profile
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The newly added ``studentinfo_shirt_type_selection`` Tag allows you to disable
the student profile question that asks about shirt types (plain vs fitted),
while retaining the question that asks about shirt size. This complements the
existing ``teacherinfo_shirt_type_selection`` Tag, which controls the same
behavior for the teacher and volunteer profiles. For either of these Tags, set
the value to False to disable the question.

On the student profile, neither of the shirt questions appear unless the
``show_student_tshirt_size_options`` Tag is set to True. On the teacher
profile, both shirt questions appear by default, but can be simultaneously
disabled by setting the ``teacherinfo_shirt_options`` Tag to False.

Tags can be added/modified/removed from the /admin/tagdict/tag/ page of the
admin panel.

Customizing PDF letterhead
~~~~~~~~~~~~~~~~~~~~~~~~~~

UI for flushing individual caches
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Script to ask teachers to increase their class capacities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the total number of student-class-hours is lower than expected, it can be
beneficial to ask teachers if they are willing to increase their class
capacities. There is a new script which can identify all classes where the
maximum capacity (set by the teachers) is less than the maximum capacity of the
rooms they are scheduled into, and sends the teachers an email asking if they
would be willing to increase their class capacities.

Right now, the script has a hard-coded message and has no web front-end. If you
wish to use this script, email websupport@learningu.org for assistance.

Minor feature additions and bugfixes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- When viewing and downloading non-anonymous custom form responses,
  you will now be able to see the name, email, and username of each
  respondent. Previously, only the user id was displayed.

- In admin user search queries, when multiple matches are available,
  all results will always be displayed, even if there is an exact
  match. Previously, if there was a username "bob" and you searched
  for "bob", you would be immediately directed to bob's profile, even
  if there was a user with first name "Bob" (but a different
  username) that you were looking for.

- During lottery student registration, cancelling a class subject or
  the last section of a class will email and cancel the registrations
  of students who had starred that class subject, not just the
  students who ranked one of the sections.

- The script that sends comm panel emails is now more robust against failures
  that occur while the script is running. Intermittent failures should never
  prevent subsets of users from receiving an email blast; every targeted user
  should eventually receive the email.

- Signing up for volunteer shifts does not require having an account.

- Some dashboard display improvements.

- If accepting credit card payments, a summary of transactions will
  appear in the admin vitals section of the dashboard.

- Expensive database queries that used to occur during student
  registration workflows were found and eliminated. This should
  improve the performance during registration.
