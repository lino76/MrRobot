import unittest
import pytest

from vault.core import Vault
from vault.core import Program


class VaultTest(unittest.TestCase):
    # The following test have been verified using the Oracle.  They are posted
    # and verified online in the Oracle Submission
    # Oracle Submission TestName:LS - Create principle alice and set delegation, returning success try 5
    def test1_run_simple_program(self):
        prog = '''as principal admin password "admin" do
                      create principal alice "alices_password"
                      set msg = "Hi Alice. Good luck in Build-it, Break-it, Fix-it!"
                      set delegation msg admin read -> alice
                      return "success"
                  ***'''

        program = Program(prog)
        result = Vault('admin').run(program)
        assert result == '{"status":"RETURNING"}'

    # Oracle Submission TestName:LS - Create principle alice and set delegation, returning msg try 6
    def test2_run_simple_program_return(self):
        prog = '''as principal admin password "admin" do
                      create principal alice "alices_password"
                      set msg = "Assigned message to msg"
                      set delegation msg admin read -> alice
                      return msg
                  ***'''

        program = Program(prog)
        result = Vault('admin').run(program)
        assert result == '{"status":"RETURNING"}'

    # Oracle Submission TestName:LS - Create principle alice set mult var and set delegation, returning x try 2
    def test3_run_simple_program_return(self):
        prog = '''as principal admin password "admin" do
                      create principal alice "alices_password"
                      set x = "my string"
                      st y = {f1 = x, f2 = "field2"}
                      set delegation x admin read -> alice
                      return y.f1
                  ***'''

        program = Program(prog)
        result = Vault('admin').run(program)
        assert result == '{"status":"RETURNING"}'

    # Oracle Submission TestName:LS - Create principle alice and bob, set delegation to bob and return msg try 1
    def test4_run_simple_program_return(self):
        prog = '''as principal admin password "admin" do
                      create principal alice "alices_password"
                      create principal bob "bobs_password"
                      set msg = "Assigned message to msg"
                      set delegation msg admin read -> bob
                      return msg
                  ***'''

        program = Program(prog)
        result = Vault('admin').run(program)
        assert result == '{"status":"RETURNING"}'

    # Oracle Submission TestName:LS - Create principles alice/bob, set msg and delegation to alice/bob, alice return msg try 1
    def test5_run_simple_program_return(self):
        prog = '''as principal admin password "admin" do
                      create principal alice "alices_password"
                      create principal bob "bobs_password"
                      set msg = "Assigned message to msg"
                      set delegation msg admin read -> alice
                      return msg
                  ***'''

        program = Program(prog)
        result = Vault('admin').run(program)
        assert result == '{"status":"RETURNING"}'


    # Oracle Submission TestName:LS - Create principles alice/bob, set msg and delegation to alice/bob, remove delegation set to alice and return msg try 1
    def test6_run_simple_program_return(self):
        prog = '''as principal admin password "admin" do
                      create principal alice "alices_password"
                      create principal bob "bobs_password"
                      set msg = "Assigned message to msg"
                      set delegation msg admin read -> alice
                      delete delegation msg admin -> read alice
                      return msg
                  ***'''

        program = Program(prog)
        result = Vault('admin').run(program)
        assert result == '{"status":"RETURNING"}'


    # Oracle Submission TestName:Two programs: Create principle alice and set delegation for alice to read msg and principle alice, to read msg try 4
    def test7_run_simple_program_return(self):
        proga = '''as principal admin password "admin" do
                       create principal alice "alices_password"
                       set msg = "Assigned message to msg"
                       set delegation msg admin read -> alice
                       return "Success"
                  ***'''
        progb = '''as principal alice password "alices_password" do
                       return msg
                  ***'''

        programa = Program(proga)
        programb = Program(progb)
        resulta = Vault('admin').run(programa)
        resultb = Vault('alice').run(programb)
        assert resulta == '{"status":"RETURNING"}'
        assert resultb == '{"status":"RETURNING"}'


    # Oracle Submission TestName Two programs: LS - Create principles alice/bob, set msg and delegation to alice, set to bob to try and return msg try 1
    def test8_run_simple_program_return(self):
        proga = '''as principal admin password "admin" do
                       create principal alice "alices_password"
                       create principal bob "bobs_password"
                       set msg = "Assigned message to msg"
                       set delegation msg admin read -> alice
                       return "Success"
                  ***'''
        progb = '''as principal bob password "bobs_password" do
                       return msg
                  ***'''

        programa = Program(proga)
        programb = Program(progb)
        resulta = Vault('admin').run(programa)
        resultb = Vault('bob').run(programb)
        assert resulta == '{"status":"RETURNING"}'
        assert resultb == '{"status":"DENIED"}'


    # Oracle Submission TestName Two programs:LS - proga:Create principle bob, set msg and delegation to bob, return msg try. progb: principle bob, set msg with another string return msg 1
    def test9_run_simple_program_return(self):
        proga = '''as principal admin password "admin" do
                       create principal alice "alices_password"
                       create principal bob "bobs_password"
                       set msg = "Assigned message to msg"
                       set delegation msg admin read -> alice
                       return "success"
                  ***'''
        progb = '''as principal bob password "bobs_password" do
                       return msg
                  ***'''
        programa = Program(proga)
        programb = Program(progb)
        resulta = Vault('admin').run(programa)
        resultb = Vault('bob').run(programb)
        assert resulta == '{"status":"RETURNING"}'
        assert resultb == '{"status":"DENIED"}'

    # Oracle Submission TestName:LS - set records, append to records, append to records, local names with records, foreach rec in names replace "" return names 1
    def test10_run_simple_program_return(self):
        proga = '''as principal admin password "admin" do
                        create principal bob password "bobs_password
                        set msg = Assigned message to msg
                        set delegation msg admin read -> bob
                        return msg
                  ***'''
        progb = '''as principal bob password bobs_password do
                        set msg = "Another message to msg"
                        return msg
                  ***'''

        programa = Program(proga)
        programb = Program(progb)
        resulta = Vault('admin').run(programa)
        resultb = Vault('bob').run(programb)
        assert resulta == '{"status":"RETURNING"}'
        assert resultb == '{"status":"DENIED"}'

    # Oracle Submission TestName:LS - set records, append to records, append to records, local names with records, foreach rec in names replace "" return names 1
    def test11_run_simple_program_return(self):
        prog = '''as principal admin password "admin" do
                      set records = []
                      append to records with { name = "mike", date = "1-1-90" }
                      append to records with { name = "dave", date = "1-1-85" }
                      local names = records
                      foreach rec in names replacewith rec.name
                      local rec = ""
                      return names
                  ***'''
        program = Program(prog)
        result = Vault('admin').run(program)
        assert result == '{"status":"RETURNING"}'

    # Oracle Submission TestName: LS - set records, append to records, append to records, append to records, foreach rec in name replace, foreach rec in records replace, set rec return records 1
    def test12_run_simple_program_return(self):
        prog = '''as principal admin password "admin" do
                      set records = []
                      append to records with { name = "mike", date = "1-1-90" }
                      append to records with { name = "dave", date = "1-1-85" }
                      append to records with { name = "dave", date = "1-1-85" }
                      foreach rec in names replacewith rec.date
                      foreach rec in records replacewith { a="hum",b=rec }
                      set rec = ""
                      return records
                  ***'''
        program = Program(prog)
        result = Vault('admin').run(program)
        assert result == '{"status":"RETURNING"}'

    # Oracle Submission TestName:LS -set records, append to records, append to records, append to records, set var return var 1
    def test13_run_simple_program_return(self):
        prog = '''as principal admin password "admin" do
                      set records = []
                      append to records with { dude = "yes" }
                      append to records with "no"
                      set var = "a variable"
                      return var
                  ***'''

        program = Program(prog)
        result = Vault('admin').run(program)
        assert result == '{"status":"RETURNING"}'

    # Oracle Submission TestName:LS - set records, foreach replacewith  set var set newvar local var return "hi" 1
    def test14_run_simple_program_return(self):
        prog = '''as principal admin password "admin" do
                      foreach y in records replacewith "boring"
                      set var = { well = "three" }
                      set newvar = ""
                      local var = ""
                      return "hi"
                  ***'''
        program = Program(prog)
        result = Vault('admin').run(program)
        assert result == '{"status":"FAILED"}'

    # Oracle Submission TestName:LS - append to records with var, return records 1
    def test15_run_simple_program_return(self):
        prog = '''as principal admin password "admin" do
                      append to records with var
                      return "records"
                  ***'''
        program = Program(prog)
        result = Vault('admin').run(program)
        assert result == '{"status":"FAILED"}'

    # Oracle Submission TestName:LS - TestCase 1 Try 1
    def test16_run_simple_program_return(self):
        proga = '''as principal admin password "admin" do
                       create principal bob "B0BPWxxd"
                       set x = "my string"
                       set delegation x admin read -> bob
                       return x
                  ***'''
        progb = '''as principal bob password "B0BPWxxd" do
                       return x
                  ***'''
        progc = '''as principal bob password "B0BPWxxd" do
                       set x = "another string"
                       return x
                  ***'''

        programa = Program(proga)
        programb = Program(progb)
        programc = Program(progc)
        resulta = Vault('admin').run(programa)
        resultb = Vault('bob').run(programb)
        resultc = Vault('bob').run(programc)
        assert resulta == '{"status":"RETURNING"}'
        assert resultb == '{"status":"RETURNING"}'
        assert resultc == '{"status":"DDENIED"}'

    # Oracle Submission TestName:LS - TestCase 2 Try 2
    def test17_run_simple_program_return(self):
         proga = '''as principal admin password "admin" do
                       set records = []
                       append to records with { name = "mike", date = "1-1-90" }
                       append to records with { name = "dave", date = "1-1-85" }
                       local names = records
                       foreach rec in names replacewith rec.name
                       local rec = ""
                       return names
                  ***'''
         progb = '''as principal admin password "admin" do
                       set records = []
                       append to records with { name = "mike", date = "1-1-90" }
                       append to records with { name = "dave", date = "1-1-85" }
                       append to records with { date = "1-1-85" }
                       foreach rec in records replacewith rec.date
                       foreach rec in records replacewith { a="hum",b=rec }
                       set rec = ""
                       return records
                  ***'''
         programa = Program(proga)
         programb = Program(progb)
         resulta = Vault('admin').run(programa)
         resultb = Vault('admin').run(programb)
         assert resulta == '{"status":"RETURNING"}'
         assert resultb == '{"status":"RETURNING"}'

    # Oracle Submission TestName:LS - TestCase 3 Try 1
    def test18_run_simple_program_return(self):
        proga = '''as principal admin password "admin" do
                       set records = []
                       append to records with { dude = "yes" }
                       append to records with "no"
                       set var = "a variable"
                       return var
                  ***'''
        progb = '''as principal admin password "admin" do
                       foreach y in records replacewith boring
                       set var = { well = "three" }
                       set newvar = ""
                       local var = ""
                       return "hi"
                  ***'''
        progc = ''' "as principal admin password "admin" do
                       append to records with var
                       return records
                  ***'''
        progd = ''' "as principal admin password "admin" do
                       return newvar
                  ***'''
        programa = Program(proga)
        programb = Program(progb)
        programc = Program(progc)
        programd = Program(progd)
        resulta = Vault('admin').run(programa)
        resultb = Vault('admin').run(programb)
        resultc = Vault('admin').run(programc)
        resultd = Vault('admin').run(programd)
        assert resulta == '{"status":"RETURNING"}'
        assert resultb == '{"status":"FAILED"}'
        assert resultc == '{"status":"RETURNING"}'
        assert resultd == '{"status":"FAILED"}'

    # Oracle Submission TestName:LS - TestCase 4 Try 1
    def test19_run_simple_program_return(self):
        proga = '''as principal admin password "admin" do
                       set x = { f="alice", g="bob" }
                       set y = "another string"
                       set z = { f=x.f, g=y, h=x.g, i="constant" }
                       return z
                  ***'''
        progb = '''as principal admin password "admin" do
                       set z = { f="hi", g="there" }
                       set x = { f=z, g="hello" }
                       return x
                  ***'''
        progc = ''' "as principal admin password "admin" do
                       set z = { f="hi", g="there" }
                       return z.h
                  ***'''

        programa = Program(proga)
        programb = Program(progb)
        programc = Program(progc)
        resulta = Vault('admin').run(programa)
        resultb = Vault('admin').run(programb)
        resultc = Vault('admin').run(programc)
        assert resulta == '{"status":"RETURNING"}'
        assert resultb == '{"status":"FAILED"}'
        assert resultc == '{"status":"FAILED"}'

    # Oracle Submission TestName:LS - TestCase 5 Try 1
    def test20_run_simple_program_return(self):
        proga = '''as principal admin password "admin" do
                        set records = []
                        set y = { jim="beam" }
                        append to records with { name = "mike", date = "1-1-90" }
                        append to records with "dave"
                        append to records with records
                        append to records with []
                        append to records with y.jim
                        set y = []
                        return records
                  ***'''
        progb = '''as principal admin password "admin" do
                        set y = { jim="beam" }
                        append to y with "hi" // should fail since y is not a table
                        return y
                  ***'''

        programa = Program(proga)
        programb = Program(progb)
        resulta = Vault('admin').run(programa)
        resultb = Vault('admin').run(programb)
        assert resulta == '{"status":"RETURNING"}'
        assert resultb == '{"status":"FAILED"}'

    # Oracle Submission TestName:LS - TestCase 6 Try 1
    def test21_run_simple_program_return(self):
        proga = '''as principal admin password "admin" do
                        local x = { field1="joe" }
                        set y = []
                        append to y with x
                        return y
                  ***'''
        progb = '''as principal admin password "admin" do
                        return x
                  ***'''
        progc = '''as principal admin password "admin" do
                        return y
                  ***'''
        progd = '''as principal admin password "admin" do
                        local x = { field1="joe" }
                        local x = "hello"
                        return x
                  ***'''
        proge = '''as principal admin password "admin" do
                        set x = { field1="joe" }
                        local x = "hello"
                        return x
                  ***'''

        programa = Program(proga)
        programb = Program(progb)
        programc = Program(progc)
        programd = Program(progd)
        programe = Program(proge)
        resulta = Vault('admin').run(programa)
        resultb = Vault('admin').run(programb)
        resultc = Vault('admin').run(programc)
        resultd = Vault('admin').run(programd)
        resulte = Vault('admin').run(programe)
        assert resulta == '{"status":"RETURNING"}'
        assert resultb == '{"status":"FAILED"}'
        assert resultc == '{"status":"RETURNING"}'
        assert resultd == '{"status":"FAILED"}'
        assert resulte == '{"status":"FAILED"}'

    # Oracle Submission TestName:LS - TestCase 7 Try 1
    def test22_run_simple_program_return(self):
        proga = '''as principal admin password "admin" do
                        create principal bob "bob"
                        create principal alice "alice"
                        set x = "x"
                        set y = "y"
                        set delegation x admin read -> alice
                        set delegation x admin write -> alice
                        set delegation x alice read -> bob
                        return x
                  ***'''
        progb = '''as principal bob password "bob" do
                        change password bob "0123__abcXY"
                        return ""
                  ***'''
        progc = '''as principal bob password "0123__abcXY" do
                        return ""
                  ***'''
        progd = '''as principal alice password "alice" do
                        change password bob "alice"
                        return ""
                  ***'''
        proge = '''as principal admin password "admin" do
                        change password admin "0123__abcXY"
                        change password alice "bob"
                        return ""
                  ***'''
        progf = '''as principal admin password "0123__abcXY" do
                        return ""
                  ***'''
        progg = '''as principal alice password "bob" do
                        return ""
                  ***'''

        programa = Program(proga)
        programb = Program(progb)
        programc = Program(progc)
        programd = Program(progd)
        programe = Program(proge)
        programf = Program(progf)
        programg = Program(progg)
        resulta = Vault('admin').run(programa)
        resultb = Vault('admin').run(programb)
        resultc = Vault('admin').run(programc)
        resultd = Vault('admin').run(programd)
        resulte = Vault('admin').run(programe)
        resultf = Vault('admin').run(programf)
        resultg = Vault('admin').run(programg)
        assert resulta == '{"status":"RETURNING"}'
        assert resultb == '{"status":"RETURNING"}'
        assert resultc == '{"status":"RETURNING"}'
        assert resultd == '{"status":"DENIED"}'
        assert resulte == '{"status":"RETURNING"}'
        assert resultf == '{"status":"RETURNING"}'
        assert resultg == '{"status":"RETURNING"}'

    # Oracle Submission TestName:LS - TestCase 8 Try 2
    #def test23_run_simple_program_return(self):

    # Oracle Submission TestName:LS - TestCase 9 Try 1
    def test24_run_simple_program_return(self):
        proga = '''as principal admin password "admin" do
                        create principal bob "bob"
                        create principal alice "alice"
                        set x = "x"
                        set y = "y"set delegation x admin read -> alice
                        set delegation x admin write -> alice
                        set delegation x alice read -> bob
                        return x
                  ***'''
        progb = '''as principal admin password "admin" do
                        set y = []
                        append to y with { x="10", y="10" }
                        set delegation x admin delegate -> alice
                        set delegation y admin delegate -> alice
                        set delegation y admin read -> alice
                        set delegation y admin append -> alice
                        delete delegation x admin read -> bob // should have no effect
                        default delegator = alice
                        create principal charlie "charlie" // delegated alice permissions on x and y
                        return y
                  ***'''
        progc = '''as principal alice password "alice" do
                        append to y with { x="0", y="100" }
                        return y
                  ***'''
        progd = '''as principal bob password "bob" do
        return x
                  ***'''
        proge = '''as principal charlie password "charlie" do
                        append to y with "charlies"
                        append to y with x
                        return y
                  ***'''
        
        programa = Program(proga)
        programb = Program(progb)
        programc = Program(progc)
        programd = Program(progd)
        programe = Program(proge)
        resulta = Vault('admin').run(programa)
        resultb = Vault('admin').run(programb)
        resultc = Vault('admin').run(programc)
        resultd = Vault('admin').run(programd)
        resulte = Vault('admin').run(programe)
        assert resulta == '{"status":"RETURNING"}'
        assert resultb == '{"status":"RETURNING"}'
        assert resultc == '{"status":"RETURNING"}'
        assert resultd == '{"status":"DENIED"}'
        assert resulte == '{"status":"RETURNING"}'