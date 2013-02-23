#/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2011-2013, Nigel Small
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from py2neo import neo4j, ogm
import unittest


class Person(object):

    def __init__(self, email=None, name=None, age=None):
        self.email = email
        self.name = name
        self.age = age

    def __eq__(self, other):
        return self.email == other.email

    def __ne__(self, other):
        return self.email != other.email

    def __repr__(self):
        return "{0} <{1}>".format(self.name, self.email)


class ExampleCodeTestCase(unittest.TestCase):

    def setUp(self):
        neo4j.GraphDatabaseService().clear()

    def test_can_execute_example_code(self):

        from py2neo import neo4j, ogm

        class Person(object):

            def __init__(self, email=None, name=None, age=None):
                self.email = email
                self.name = name
                self.age = age

            def __str__(self):
                return self.name

        graph_db = neo4j.GraphDatabaseService()
        store = ogm.Store(graph_db)

        alice = Person("alice@example.com", "Alice", 34)
        store.save_unique(alice, "People", "email", alice.email)

        bob = Person("bob@example.org", "Bob", 66)
        carol = Person("carol@example.net", "Carol", 42)
        store.relate(alice, "LIKES", bob)
        store.relate(alice, "LIKES", carol)
        store.save(alice)

        friends = store.load_related(alice, "LIKES", Person)
        print("Alice likes {0}".format(" and ".join(str(f) for f in friends)))


class RelateTestCase(unittest.TestCase):

    def setUp(self):
        self.graph_db = neo4j.GraphDatabaseService()
        self.graph_db.clear()
        self.store = ogm.Store(self.graph_db)

    def test_can_relate_to_other_object(self):
        alice = Person("alice@example.com", "Alice", 34)
        bob = Person("bob@example.org", "Bob", 66)
        self.store.relate(alice, "LIKES", bob)
        assert hasattr(alice, "__rel__")
        assert isinstance(alice.__rel__, dict)
        assert "LIKES" in alice.__rel__
        assert alice.__rel__["LIKES"] == [({}, bob)]

    def test_can_relate_to_other_object_with_properties(self):
        alice = Person("alice@example.com", "Alice", 34)
        bob = Person("bob@example.org", "Bob", 66)
        self.store.relate(alice, "LIKES", bob, {"since": 1999})
        assert hasattr(alice, "__rel__")
        assert isinstance(alice.__rel__, dict)
        assert "LIKES" in alice.__rel__
        assert alice.__rel__["LIKES"] == [({"since": 1999}, bob)]


class SeparateTestCase(unittest.TestCase):

    def setUp(self):
        self.graph_db = neo4j.GraphDatabaseService()
        self.graph_db.clear()
        self.store = ogm.Store(self.graph_db)

    def test_can_separate_from_other_objects(self):
        alice = Person("alice@example.com", "Alice", 34)
        bob = Person("bob@example.org", "Bob", 66)
        carol = Person("carol@example.net", "Carol", 42)
        self.store.relate(alice, "LIKES", bob)
        self.store.relate(alice, "LIKES", carol)
        self.store.separate(alice, "LIKES", carol)
        assert alice.__rel__["LIKES"] == [({}, bob)]
        self.store.separate(alice, "LIKES", bob)
        assert alice.__rel__["LIKES"] == []

    def test_nothing_happens_if_unknown_rel_type_supplied(self):
        alice = Person("alice@example.com", "Alice", 34)
        bob = Person("bob@example.org", "Bob", 66)
        self.store.relate(alice, "LIKES", bob)
        self.store.separate(alice, "DISLIKES", bob)
        assert alice.__rel__["LIKES"] == [({}, bob)]

    def test_nothing_happens_if_unknown_endpoint_supplied(self):
        alice = Person("alice@example.com", "Alice", 34)
        bob = Person("bob@example.org", "Bob", 66)
        carol = Person("carol@example.net", "Carol", 42)
        self.store.relate(alice, "LIKES", bob)
        self.store.separate(alice, "LIKES", carol)
        assert alice.__rel__["LIKES"] == [({}, bob)]


class LoadRelatedTestCase(unittest.TestCase):

    def setUp(self):
        self.graph_db = neo4j.GraphDatabaseService()
        self.graph_db.clear()
        self.store = ogm.Store(self.graph_db)

    def test_can_load_single_related_object(self):
        alice = Person("alice@example.com", "Alice", 34)
        bob = Person("bob@example.org", "Bob", 66)
        self.store.relate(alice, "LIKES", bob)
        self.store.save(alice)
        friends = self.store.load_related(alice, "LIKES", Person)
        assert friends == [bob]

    def test_can_load_multiple_related_objects(self):
        alice = Person("alice@example.com", "Alice", 34)
        bob = Person("bob@example.org", "Bob", 66)
        carol = Person("carol@example.net", "Carol", 42)
        self.store.relate(alice, "LIKES", bob)
        self.store.relate(alice, "LIKES", carol)
        self.store.save(alice)
        friends = self.store.load_related(alice, "LIKES", Person)
        assert friends == [bob, carol]

    def test_can_load_related_objects_among_other_relationships(self):
        alice = Person("alice@example.com", "Alice", 34)
        bob = Person("bob@example.org", "Bob", 66)
        carol = Person("carol@example.net", "Carol", 42)
        dave = Person("dave@example.co.uk", "Dave", 18)
        self.store.relate(alice, "LIKES", bob)
        self.store.relate(alice, "LIKES", carol)
        self.store.relate(alice, "DISLIKES", dave)
        self.store.save(alice)
        print(alice.__node__)
        friends = self.store.load_related(alice, "LIKES", Person)
        assert friends == [bob, carol]
        enemies = self.store.load_related(alice, "DISLIKES", Person)
        assert enemies == [dave]


class LoadTestCase(unittest.TestCase):
    pass


class LoadIndexedTestCase(unittest.TestCase):
    pass


class LoadUniqueTestCase(unittest.TestCase):

    def setUp(self):
        self.graph_db = neo4j.GraphDatabaseService()
        self.graph_db.clear()
        self.store = ogm.Store(self.graph_db)

    def test_can_load_simple_object(self):
        alice_node = self.graph_db.get_or_create_indexed_node("People", "email", "alice@example.com", {
            "email": "alice@example.com",
            "name": "Alice Allison",
            "age": 34,
        })
        alice = self.store.load_unique(Person, "People", "email", "alice@example.com")
        assert isinstance(alice, Person)
        assert hasattr(alice, "__node__")
        assert alice.__node__ == alice_node
        assert hasattr(alice, "__rel__")
        assert alice.__rel__ == {}
        assert alice.email == "alice@example.com"
        assert alice.name == "Alice Allison"
        assert alice.age == 34

    def test_can_load_object_with_relationships(self):
        alice_node = self.graph_db.get_or_create_indexed_node("People", "email", "alice@example.com", {
            "email": "alice@example.com",
            "name": "Alice Allison",
            "age": 34,
        })
        path = alice_node.create_path("LIKES", {"name": "Bob Robertson"})
        bob_node = path.nodes[1]
        alice = self.store.load_unique(Person, "People", "email", "alice@example.com")
        assert isinstance(alice, Person)
        assert hasattr(alice, "__node__")
        assert alice.__node__ == alice_node
        assert hasattr(alice, "__rel__")
        assert alice.__rel__ == {
            "LIKES": [({}, bob_node)],
        }
        assert alice.email == "alice@example.com"
        assert alice.name == "Alice Allison"
        assert alice.age == 34
        friends = self.store.load_related(alice, "LIKES", Person)
        assert isinstance(friends, list)
        assert len(friends) == 1
        friend = friends[0]
        assert isinstance(friend, Person)
        assert friend.__node__ == bob_node
        enemies = self.store.load_related(alice, "DISLIKES", Person)
        assert isinstance(enemies, list)
        assert len(enemies) == 0


class ReloadTestCase(unittest.TestCase):
    pass


class SaveTestCase(unittest.TestCase):
    pass


class SaveIndexedTestCase(unittest.TestCase):
    pass


class SaveUniqueTestCase(unittest.TestCase):

    def setUp(self):
        self.graph_db = neo4j.GraphDatabaseService()
        self.graph_db.clear()
        self.store = ogm.Store(self.graph_db)

    def test_can_save_simple_object(self):
        alice = Person("alice@example.com", "Alice", 34)
        self.store.save_unique(alice, "People", "email", "alice@example.com")
        assert hasattr(alice, "__node__")
        assert isinstance(alice.__node__, neo4j.Node)
        assert alice.__node__ == self.graph_db.get_indexed_node("People", "email", "alice@example.com")

    def test_can_save_object_with_rels(self):
        alice = Person("alice@example.com", "Alice Allison", 34)
        bob_node, carol_node = self.graph_db.create(
            {"name": "Bob"},
            {"name": "Carol"},
        )
        alice.__rel__ = {"KNOWS": [({}, bob_node)]}
        self.store.save_unique(alice, "People", "email", "alice@example.com")
        assert hasattr(alice, "__node__")
        assert isinstance(alice.__node__, neo4j.Node)
        assert alice.__node__ == self.graph_db.get_indexed_node("People", "email", "alice@example.com")
        print(alice.__node__, bob_node, carol_node, alice.__node__.match())
        alice.__rel__ = {"KNOWS": [({}, bob_node), ({}, carol_node)]}
        self.store.save_unique(alice, "People", "email", "alice@example.com")
        print(alice.__node__, bob_node, carol_node, alice.__node__.match())


class DeleteTestCase(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()