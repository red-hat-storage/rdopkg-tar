#!/usr/bin/python3

import argparse

from rdopkg.utils import log
from rdopkg.utils import specfile
from rdopkg.utils.cmd import run
from rdopkg.utils.git import git
from rdopkg import guess
import rdopkg.actions.distgit.actions
import os


def diff_filenames(base, branch):
    """ List all files changed between this "base" and this "branch". """
    range_ = '%s..%s' % (base, branch)
    diff_output = git('diff',
                      '--name-only',
                      '--diff-filter=ACMRTUXB',  # exclude "D" for deletes.
                      '-z',
                      range_, print_stdout=False)
    filenames = [f for f in diff_output.split("\0") if f]
    return filenames


def archive_files(basename, sha, filenames):
    """
    Archive a list of files from this branch into a "-changes" tarball.

    :param basename: base name of the archive tarball.
    :param sha: Git sha1 where the files reside.
    :param filenames: list of files to archive.
    """
    try:
        int(sha, 16)
    except ValueError:
        raise ValueError('%s does not look like a sha1' % sha)
    output = '%s-%s-changes.tar.gz' % (basename, sha)
    # return
    git('archive',
        '--prefix=%s/' % basename,
        '--output=%s' % output,
        sha,
        *filenames,
        log_cmd=False, print_stdout=False)
    return output


def set_source1(spec):
    """ Ensure Source1 is our -changes tarball. """
    source_value = '%{name}-%{version}-%{commit}-changes.tar.gz'
    # This get_tag() will raise if Source1 is not present:
    source1 = spec.get_tag('Source1', expand_macros=False)
    if source1 != source_value:
        # Log the existing Source1, then clobber it.
        msg = 'overwriting Source1: %s with new -changes.tar.gz' % source1
        log.warn(msg)
        spec.set_tag('Source1', source_value)


def check_new_commits(base, old, new):
    """
    Determine the set of changes between "old" and "new" commits.

    Kind of similar to rdopkg's check_new_patches()

    :param base: common Git ref between "old" and "new", eg. v12.2.8
    :param old: old Git sha1
    :param new: new Git sha1
    """
    if old == new:
        return []
    hashes = git.get_commit_hashes(base, new)
    hashlen = len(hashes[0])
    if old[:hashlen] in hashes:
        # This is a linear change. We can simply return the Git commit
        # subjects between "old" and "new".
        changes_data = git.get_commit_bzs(old, new)
        return format_changelog(changes_data)
    else:
        # This is not a linear change (a developer rewrote history).
        return ['Update patches']
        # TODO: find common ancestor, and figure out what diverged.
        # Need to think more about this.
        # https://github.com/softwarefactory-project/rdopkg/issues/160


def format_changelog(changes_data):
    """
    Return a list of lines for an RPM %changelog.

    :param list changes: a list of tuples: sha, subject, and list-of-bzs.
    :returns: a human-readable list of changes with RHBZs.
    """
    changes = []
    for _, subj, bzs in changes_data:
        bzstr = ' '.join(map(lambda x: 'rhbz#%s' % x, bzs))
        if bzstr:
            subj += ' (%s)' % bzstr
        changes.append(subj)
    return changes


def clear_old_changes_sources():
    """ Delete the "-changes.tar.gz" lines from the "sources" file. """
    with open('sources', 'r') as f:
        lines = f.readlines()
    with open('sources', 'w') as f:
        for line in lines:
            if '-changes.tar.gz' not in line:
                f.write(line)


def commit_distgit_amend(suffix):
    """
    Amend commit with original gitlab user

    :param suffix: String to be amended to commit.
    """
    rng = 'HEAD~..HEAD'
    message = git('log', '--format=%s%n%n%b', rng, log_cmd=False)
    message += '\n\n' + suffix
    cmd = ['commit', '-a', '-F', '-', '--amend']
    git(*cmd, input=message, print_output=True)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--patches-branch',
        help='Specify another local "patches" branch, like "ceph-5.0-rhel-patches-bz12345"',
    )
    args = parser.parse_args()
    spec = specfile.Spec()

    name = spec.get_tag('Name', expand_macros=True)  # "ceph"
    version = spec.get_tag('Version', expand_macros=True)  # "12.2.8"
    orig_commit = spec.get_macro('commit')  # "9e20ef1b14ac70dea53123"

    branch = git.current_branch()  # "ceph-3.2-rhel-7"
    tag_style = guess.version_tag_style(version=version)  # "vX.Y.Z"
    base_tag = guess.version2tag(version, tag_style)  # "v12.2.8"
    osdist = guess.osdist()

    # "ceph-3.2-rhel-patches"
    if args.patches_branch:
        patches_branch = args.patches_branch
    else:
        remote_patches_branch = guess.patches_branch(branch, pkg=name,
                                                     osdist=osdist)
        patches_branch = remote_patches_branch.partition('/')[2]

    patches_sha = git('rev-parse', patches_branch)  # "9e20ef1b14ac70dea53123"

    archive_basename = '%s-%s' % (name, version)  # "ceph-12.2.8"
    patches_base, patches_base_commits = spec.get_patches_base()
    if patches_base_commits != 0:
        # We don't yet support the "+n_commits" syntax for patches_base.
        raise NotImplementedError('use a plain ref in patches_base')
    if patches_base is None:
        patches_base = base_tag
    filenames = diff_filenames(patches_base, patches_branch)
    if not filenames:
        # todo: make this a silent no-op eventually
        log.warning('%s identical to %s' % (patches_branch, patches_base))
        raise RuntimeError(patches_base)

    tarball = archive_files(archive_basename, patches_sha, filenames)
    log.info('wrote %s' % tarball)

    # Ensure our spec file will reference this tarball.
    spec.set_macro('commit', patches_sha)
    set_source1(spec)
    spec.save()

    # Find the changelog entries from the Git -patches branch.
    changes = check_new_commits(patches_base, orig_commit, patches_sha)

    if not changes:
        log.info('no changes. exiting')
        raise SystemExit(1)

    # Bump the release and add the %changelog entries.

    # Insert %changelog.
    rdopkg.actions.distgit.actions.update_spec(branch=branch, changes=changes)

    # add + upload this new tarball.
    if guess.new_sources():
        fedpkg = 'fedpkg'
        if osdist.startswith('RH'):
            fedpkg = 'rhpkg'
        clear_old_changes_sources()
        run(fedpkg, 'upload', tarball, direct=True)

    # Commit everything to dist-git
    rdopkg.actions.distgit.actions.commit_distgit_update(branch=branch,
                                                         local_patches_branch=patches_branch)

    # Check for the original commiter username in jenkins env variables.
    # If it exists, then amend a suffix to the commit.
    userName = os.environ.get('gitlabUserName')
    gitlabuserName = os.environ.get('gitlabUserUsername')

    if userName or gitlabuserName:
        commit_distgit_amend(suffix="GitLab-User: " + gitlabuserName + " " + userName)

    # Show the final commit
    rdopkg.actions.distgit.actions.final_spec_diff(branch=branch)


if __name__ == '__main__':
    main()
