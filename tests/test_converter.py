#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File name: test_converter.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg.
#   Copyright 2016-2017 VideoMorph Development Team

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""This module provides tests for conversionlib.py module."""

import nose
from PyQt5.QtCore import QProcess

from videomorph.converter import media
from videomorph.converter.conversionlib import ConversionLib
from videomorph.converter.profile import ConversionProfile


class TestConversionLib:
    conv_lib = ConversionLib()

    profile = ConversionProfile(prober=conv_lib.prober_path)
    profile.update(new_quality='FLV Fullscreen 320x240 (4:3)')

    media_list = media.MediaList(profile)

    @classmethod
    def setUpClass(cls):
        gen = cls.media_list.populate(('Dad.mpg',))
        next(gen)
        next(gen)

    @classmethod
    def tearDownClass(cls):
        cls.media_list.get_file(0).delete_output('.', tagged_output=True)

    def get_conversion_cmd(self):
        """Return a conversion command."""
        cmd = self.media_list.get_file(position=0).build_conversion_cmd(
            output_dir='.',
            subtitle=False,
            tagged_output=True,
            target_quality='FLV Fullscreen 320x240 (4:3)')
        return cmd

    def test_get_library_path(self):
        """Test ConversionLib.library_path."""
        assert self.conv_lib.library_path in {'/usr/bin/ffmpeg',
                                              '/usr/local/bin/ffmpeg'}

    def test_prober_path(self):
        """Test the ConversionLib.prober_path."""
        assert self.conv_lib.prober_path in {'/usr/bin/ffprobe',
                                             '/usr/local/bin/ffprbe'}

    def test_start_converter(self):
        """Test ConversionLib.start_converter()."""
        self.conv_lib.start_converter(cmd=self.get_conversion_cmd())

        assert self.conv_lib.converter_state() == QProcess.Starting
        self.conv_lib.stop_converter()

    def test_read_converter_output(self):
        """Test ConversionLib.read_converter_output()."""
        self.conv_lib.start_converter(cmd=self.get_conversion_cmd())
        assert len(self.conv_lib.read_converter_output())
        self.conv_lib.stop_converter()

    def test_catch_library_error_true(self):
        """Test _OutputReader.catch_library_error() -> true."""
        self.conv_lib.reader.update_read('Some random output with '
                                         'Unknown encoder error')
        assert self.conv_lib.reader.catch_library_error() == 'Unknown encoder'

    def test_catch_library_error_false(self):
        """Test _OutputReader.catch_library_error() -> false."""
        self.conv_lib.reader.update_read('Some random output with '
                                         'no error')
        assert self.conv_lib.reader.catch_library_error() is None

    def test_stop_converter(self):
        """Test ConversionLib.stop_converter()."""
        self.conv_lib.stop_converter()
        assert not self.conv_lib.converter_is_running


if __name__ == '__main__':
    nose.run()
