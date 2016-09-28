import unittest
import pytest

from vault.core import Datastore
from vault.util import Principal


class DatastoreTest(unittest.TestCase):

    def test_set(self):
        # TODO should be a fixture
        datastore = Datastore()
        context = datastore.create_context(Principal("bob", "password"))
        # Actual test
        datastore.set("x", 2)
        result = datastore.commit()
        assert result[0] == {'SET'}

    def test_get(self):
        # TODO should be a fixture
        datastore = Datastore()
        context = datastore.create_context(Principal("bob", "password"))
        # Actual test
        datastore.set("x", 2)
        datastore.get("x")
        result = datastore.commit()
        assert result[0] == {'SET'}
        assert result[1] == {'GET', 2}

    def test_append(self):
        pass



