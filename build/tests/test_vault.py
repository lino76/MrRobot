import unittest
import pytest

from vault.core import Vault
from vault.core import Program


class VaultTest(unittest.TestCase):

    def test_run_simple_program(self):
        prog = '''as principal admin password "admin" do
                      create principal alice "alices_password"
                      set msg = "Hi Alice. Good luck in Build-it, Break-it, Fix-it!"
                      set delegation msg admin read -> alice
                      return "success"
                  ***'''
        program = Program(prog)
        result = Vault('admin').run(program)
        assert result == '{"status":"FAILURE"}'

