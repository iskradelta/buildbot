# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members

import io
import os
import sys

from buildworker.scripts import base
from buildworker.test.util import misc
from twisted.trial import unittest


class TestIsBuildworkerDir(misc.FileIOMixin, misc.LoggingMixin, unittest.TestCase):

    """Test buildworker.scripts.base.isBuildworkerDir()"""

    def setUp(self):
        # capture output to stdout
        self.mocked_stdout = io.BytesIO()
        self.patch(sys, "stdout", self.mocked_stdout)

        self.setUpLogging()

        # generate OS specific relative path to buildbot.tac inside basedir
        self.tac_file_path = os.path.join("testdir", "buildbot.tac")

    def assertReadErrorMessage(self, strerror):

        self.assertLogged("error reading '%s': %s" % (self.tac_file_path, strerror),
                          "invalid buildworker directory 'testdir'")

    def test_open_error(self):
        """Test that open() errors are handled."""

        # patch open() to raise IOError
        self.setUpOpenError(1, "open-error", "dummy")

        # check that isBuildworkerDir() flags directory as invalid
        self.assertFalse(base.isBuildworkerDir("testdir"))

        # check that correct error message was printed to stdout
        self.assertReadErrorMessage("open-error")

        # check that open() was called with correct path
        self.open.assert_called_once_with(self.tac_file_path)

    def test_read_error(self):
        """Test that read() errors on buildbot.tac file are handled."""

        # patch open() to return file object that raises IOError on read()
        self.setUpReadError(1, "read-error", "dummy")

        # check that isBuildworkerDir() flags directory as invalid
        self.assertFalse(base.isBuildworkerDir("testdir"))

        # check that correct error message was printed to stdout
        self.assertReadErrorMessage("read-error")

        # check that open() was called with correct path
        self.open.assert_called_once_with(self.tac_file_path)

    def test_unexpected_tac_contents(self):
        """Test that unexpected contents in buildbot.tac is handled."""

        # patch open() to return file with unexpected contents
        self.setUpOpen("dummy-contents")

        # check that isBuildworkerDir() flags directory as invalid
        self.assertFalse(base.isBuildworkerDir("testdir"))

        # check that correct error message was printed to the log
        self.assertLogged("unexpected content in '%s'" % self.tac_file_path,
                         "invalid buildworker directory 'testdir'",
                         "unexpected error message on stdout")
        # check that open() was called with correct path
        self.open.assert_called_once_with(self.tac_file_path)

    def test_workerdir_good(self):
        """Test checking valid buildworker directory."""

        # patch open() to return file with valid buildworker tac contents
        self.setUpOpen("Application('buildworker')")

        # check that isBuildworkerDir() flags directory as good
        self.assertTrue(base.isBuildworkerDir("testdir"))

        # check that open() was called with correct path
        self.open.assert_called_once_with(self.tac_file_path)
