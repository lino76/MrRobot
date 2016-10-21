import unittest
import pytest
import random
import string

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

    def test_validate_port_longpass(self):
        password = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(65535 + 1))
        input = [1024, password]
        with pytest.raises(VaultError):
            commandline.validate_args(input)

    # TestArg1
    def test_validate_port_testarg1(self):
        input = ['06300']
        with pytest.raises(VaultError):
            commandline.validate_args(input)

    # TestArg2
    def test_validate_port_testarg2(self):
        input = ['014234']
        with pytest.raises(VaultError):
            commandline.validate_args(input)

    # TestArg3
    def test_validate_port_testarg3(self):
        input = ['0x189C']
        with pytest.raises(VaultError):
            commandline.validate_args(input)

    # TestArg4
    def test_validate_port_testarg4(self):
        input = [' 6300']
        with pytest.raises(VaultError):
            commandline.validate_args(input)

    # TestArg5
    def test_validate_port_testarg5(self):
        input = ['6300 ']
        with pytest.raises(VaultError):
            commandline.validate_args(input)

    # TestArg6
    def test_validate_port_testarg6(self):
        input = ['1023']
        with pytest.raises(VaultError):
            commandline.validate_args(input)

    # TestArg7
    def test_validate_port_testarg7(self):
        input = ['65536']
        with pytest.raises(VaultError):
            commandline.validate_args(input)