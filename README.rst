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
| Does not require the ``%commit``   | Requires the ``%commit`` macro   |
| macro in your spec file in order   | in your spec file in order to    |
| to generate the ``%changelog``.    | generate the ``%changelog``.     |
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

Understanding branches
======================

We build RH Ceph Storage in ``ceph-*`` Git branches.
**dist-git branches** follow the form ``<product-name>-<product-version>-<OS>-<OS version>``.

For RH Ceph Storage 5, we support both RHEL 8 and RHEL 9, so we have the following branches:

* ``ceph-5.0-rhel-8``: The first release of the RHCEPH 5 product. We did not support RHEL 9 yet because it was so early.
* ``ceph-5.1-rhel-8`` and ``ceph-5.1-rhel-9``: The second release of the RHCEPH 5 product. We started building Ceph for RHEL 9.
* ``ceph-5.2-rhel-8`` and ``ceph-5.2-rhel-9``: The third release of the RHCEPH 5 product. 

For patch management, we use  rdopkg_ **-style "-patches" branches** 
that follow a similar convention. Note, we do not have separate "rhel-8" or "rhel-9" -patches branches, 
because the code should be identical on both OSes.

RH Ceph Storage 5:

* ``ceph-5.0-rhel-patches``: RHCEPH 5.0 downstream code.
* ``ceph-5.1-rhel-patches``: RHCEPH 5.1 downstream code.
* ``ceph-5.2-rhel-patches``: RHCEPH 5.2 downstream code.
* ``ceph-5.3-rhel-patches``: RHCEPH 5.3 downstream code.
