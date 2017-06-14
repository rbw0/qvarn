# transaction_tests.py - unit tests
#
# Copyright 2015, 2016 Suomen Tilaajavastuu Oy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import unittest

import qvarn


class TransactionTests(unittest.TestCase):

    def setUp(self):
        self.sql = DummyAdapter()
        self.trans = qvarn.Transaction()
        self.trans.set_sql(self.sql)

    def test_creates_a_table(self):
        with self.trans:
            self.trans.create_table(u'foo', {u'bar': int})
        self.assertEqual(
            self.sql.created_tables,
            {u'foo': {u'bar': int}})

    def test_adds_a_column(self):
        with self.trans:
            self.trans.create_table(u'foo', {u'bar': int})
            self.trans.add_column(u'foo', u'bar2', int)
        self.assertEqual(
            self.sql.altered_tables,
            {u'foo': {u'bar2': int}})

    def test_renames_a_table(self):
        with self.trans:
            self.trans.create_table(u'foo', {u'bar': int})
            self.trans.rename_table(u'foo', u'foobar')
        self.assertEqual(self.sql.renamed_tables, {u'foo': u'foobar'})

    def test_drops_a_table(self):
        with self.trans:
            self.trans.create_table(u'foo', {u'bar': int})
            self.trans.drop_table(u'foo')
        self.assertEqual(self.sql.dropped_tables, [u'foo'])

    def test_selects(self):
        with self.trans:
            self.trans.create_table(u'foo', {u'bar': int})
            self.trans.select(u'foo', [u'bar'], ('=', u'foo', u'bar', 0))
        self.assertEqual(self.sql.selected_tables, [u'foo'])

    def test_selects_complex_condition(self):
        with self.trans:
            self.trans.create_table(u'foo', {u'bar': int})
            self.trans.create_table(u'foo2', {u'bar2': int})
            self.trans.select(
                u'foo', [u'bar'],
                ('OR', ('=', u'foo', u'bar', 0), ('=', u'foo2', u'bar2', 0)))
        self.assertEqual(self.sql.selected_tables, [u'foo'])

    def test_inserts(self):
        with self.trans:
            self.trans.create_table(u'foo', {u'bar': int})
            self.trans.insert(u'foo', {u'bar': 42})
            rows = self.trans.select(u'foo', [u'bar'], None)
        self.assertEqual(self.sql.inserted_tables, [u'foo'])
        self.assertEqual(rows, [{u'bar': 42}])

    def test_updates(self):
        with self.trans:
            self.trans.create_table(u'foo', {u'bar': int})
            self.trans.insert(u'foo', {u'bar': 42})
            self.trans.update(u'foo', None, {u'bar': 7})
            rows = self.trans.select(u'foo', [u'bar'], None)
        self.assertEqual(self.sql.updated_tables, [u'foo'])
        self.assertEqual(rows, [{u'bar': 7}])

    def test_deletes(self):
        with self.trans:
            self.trans.create_table(u'foo', {u'bar': int})
            self.trans.insert(u'foo', {u'bar': 42})
            self.trans.delete(u'foo', ('=', u'foo', u'bar', 42))
            rows = self.trans.select(u'foo', [u'bar'], None)
        self.assertEqual(self.sql.deleted_tables, [u'foo'])
        self.assertEqual(rows, [])


class DummyAdapter(qvarn.SqliteAdapter):

    def __init__(self):
        super(DummyAdapter, self).__init__()
        self.created_tables = {}
        self.altered_tables = {}
        self.renamed_tables = {}
        self.dropped_tables = []
        self.selected_tables = []
        self.inserted_tables = []
        self.updated_tables = []
        self.deleted_tables = []

    def format_create_table(self, table_name, column_name_types):
        assert table_name not in self.created_tables
        self.created_tables[table_name] = column_name_types
        return self._call(
            'format_create_table', table_name, column_name_types)

    def format_add_column(self, table_name, column_name, column_type):
        assert table_name not in self.altered_tables
        self.altered_tables[table_name] = {column_name: column_type}
        return self._call(
            'format_add_column', table_name, column_name, column_type)

    def format_rename_table(self, old_name, new_name):
        assert old_name not in self.renamed_tables
        self.renamed_tables[old_name] = new_name
        return self._call('format_rename_table', old_name, new_name)

    def format_drop_table(self, table_name):
        self.dropped_tables.append(table_name)
        return self._call('format_drop_table', table_name)

    def format_select(self, table_name, column_names, select_conditions):
        self.selected_tables.append(table_name)
        return self._call(
            'format_select', table_name, column_names, select_conditions)

    def format_insert(self, table_name, column_name_values):
        self.inserted_tables.append(table_name)
        return self._call(
            'format_insert', table_name, column_name_values)

    def format_update(self, table_name, select_conditions, column_name_values):
        self.updated_tables.append(table_name)
        return self._call(
            'format_update', table_name, select_conditions, column_name_values)

    def format_delete(self, table_name, select_conditions):
        self.deleted_tables.append(table_name)
        return self._call('format_delete', table_name, select_conditions)

    def _call(self, method_name, *args, **kwargs):
        method = getattr(super(DummyAdapter, self), method_name)
        return method(*args, **kwargs)
