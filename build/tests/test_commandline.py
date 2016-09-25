import unittest
import pytest

from vault.cmd import commandline
from vault.error import VaultError


class CommmandlineTest(unittest.TestCase):

    # These tests check validate_args method of the commandline class
    def test_validate_noport_nopass(self):
        input = []
        with pytest.raises(VaultError):
            commandline.validate_args(input)

    def test_validate_lowport_nopass(self):
        input = [10]
        with pytest.raises(VaultError):
            commandline.validate_args(input)

    def test_validate_highport_nopass(self):
        input = [100000]
        with pytest.raises(VaultError):
            commandline.validate_args(input)

    def test_validate_octalport_nopass(self):
        input = [oct(64)]
        with pytest.raises(VaultError):
            commandline.validate_args(input)

    def test_validate_hexport_nopass(self):
        input = ['0x400']
        with pytest.raises(VaultError):
            commandline.validate_args(input)

    def test_validate_noport_withpass(self):
        input = ['admin']
        with pytest.raises(VaultError):
            commandline.validate_args(input)

    def test_validate_port_nopass(self):
        input = [1024]
        assert commandline.validate_args(input) == [1024, 'admin']

    def test_validate_port_goodpass(self):
        input = [1024, 'password']
        assert commandline.validate_args(input) == [1024, 'password']

    def test_validate_port_invalidpass(self):
        input = [1024, '~%password']
        with pytest.raises(VaultError):
            commandline.validate_args(input)

    def test_validate_port_invalidpass_longer(self):
        input = [1024, 'password~!@#$%^&*()_+=']
        with pytest.raises(VaultError):
            commandline.validate_args(input)

    #TODO test a password greater than 65535