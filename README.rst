rdopkg tar-changes
==================

This is a tool that works in a similar way to ``rdopkg patch``. It uses
rdopkg_'s APIs to tar up all the changes in the Git -patches branch into a
"-changes.tar.gz" tarball and adds the tarball to the RPM packaging.

I use this to combine all our downstream changes into a single file suitable
for dist-git.

Comparing ``rdopkg patch`` with this ``tar-changes`` script:

+------------------------------------+----------------------------------+
| "rdopkg patch"                     | this "tar-changes" script        |
+====================================+==================================+
| Transforms a downstream -patches branch into output suitable for      |
| dist-git                                                              |
+------------------------------------+----------------------------------+
| Operates in conjuction with an unchanging upstream tarball            |
+------------------------------------+----------------------------------+
| Applies changes during the `%prep` stage of rpmbuild                  |
+------------------------------------+----------------------------------+
| Generates .patch files             | Generates a tarball of changed   |
|                                    | files                            |
+------------------------------------+----------------------------------+
| Limited_ by RHEL 7's static        | rpmbuild's ``%prep`` script does |
| buffer limit for ``%prep`` in      | not grow with the number of      |
| rpmbuild.                          | patches.                         |
+------------------------------------+----------------------------------+
| Ability to delete files entirely   | Unable to delete files (only add |
| from the tree downstream.          | or edit existing files).         |
+------------------------------------+----------------------------------+
| Unable to edit binary files        | Able to apply edits to binary    |
|                                    | files                            |
+------------------------------------+----------------------------------+
| Does not require the %commit macro | Requires the %commit macro in    |
| in your spec file in order to      | your spec file in order to       |
| generate the %changelog.           | generate the %changelog.         |
+------------------------------------+----------------------------------+
| Slightly more visibility into      | Slightly less visibility into    |
| changes when browsing dist-git,    | changes when browsing dist-git,  |
| since you can see the individual   | since you only see a tarball and |
| .patch files changing.             | Git sha1 changing.               |
+------------------------------------+----------------------------------+
| To reconstruct a -patches branch   | No simple way to reconstruct a   |
| commit-by-commit, without the ref  | -patches branch if a ref is      |
| or sha1, use ``git am``            | dangling/lost. More important    |
|                                    | to tag every -patches branch     |
|                                    | change with                      |
|                                    | ``rdopkg tag-patches``.          |
+------------------------------------+----------------------------------+

.. _rdopkg: https://github.com/softwarefactory-project/rdopkg
.. _Limited: https://github.com/softwarefactory-project/rdopkg/issues/169
