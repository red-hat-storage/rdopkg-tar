import os
import importlib.machinery
import importlib.util
import py.path
import pytest

loader = importlib.machinery.SourceFileLoader('tarchanges', 'tar-changes')
spec = importlib.util.spec_from_loader(loader.name, loader)
tarchanges = importlib.util.module_from_spec(spec)
loader.exec_module(tarchanges)


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(TESTS_DIR, 'fixtures')


def test_clear_old_changes_sources(tmpdir, monkeypatch):
    # Copy our "sources" fixture file to a tmpdir.
    fixtures_dir = py.path.local(FIXTURES_DIR)
    fixtures_dir.join('sources').copy(tmpdir)
    monkeypatch.chdir(tmpdir)
    # Test clear_old_changes_sources().
    tarchanges.clear_old_changes_sources()
    sources = tmpdir.join('sources')
    expected = '3a393d427d5b16c33cf24da91244cc7a  ceph-12.2.8.tar.gz\n'
    sources.read() == expected


@pytest.mark.parametrize("test_input,expected", [
    ('master', 'RDO'),
    ('ceph-5.0-rhel-8', 'RHCEPH'),
    ('private-kdreyer-ceph-5.0-rhel-8', 'RHCEPH'),
])
def test_guess_osdist(monkeypatch, test_input, expected):
    monkeypatch.setattr(tarchanges.guess, 'current_branch', lambda: test_input)
    result = tarchanges.guess_osdist()
    assert result == expected
