from db import get_cursor
from db.exceptions import (
    NotFoundError
)


def lazy(method):
    def wrapper(self, *args, **kwargs):
        self._load()
        return method(self, *args, **kwargs)

    wrapper.__name__ = method.__name__
    return wrapper


class Model(object):
    delete_query    = 'DELETE FROM "{table}" WHERE id=%s'
    insert_query    = 'INSERT INTO "{table}" ({columns}) VALUES ({placeholders}) RETURNING id'
    list_query      = 'SELECT * FROM "{table}"'
    parent_query    = 'SELECT * FROM "{table}" WHERE {parent}_id=%s'
    select_query    = 'SELECT * FROM "{table}" WHERE id=%s'
    sibling_query   = 'SELECT * FROM "{sibling}" NATURAL JOIN "{join_table}" WHERE {table}_id=%s'
    update_children = 'UPDATE "{table}" SET {parent}_id=%s WHERE {table}_id IN ({children})'
    update_query    = 'UPDATE "{table}" SET {columns} WHERE {table}_id=%s'

    def __init__(self, id=None):
        self._cursor   = get_cursor
        self._fields   = {}
        self._id       = id
        self._loaded   = False
        self._modified = False
        self._class    = self.__class__.__name__
        self._table    = self.__class__.__name__.lower()

    @property
    def id(self):
        return self._id

    @property
    @lazy
    def created(self):
        return self._fields['created']

    @property
    @lazy
    def updated(self):
        self._load()
        return self._fields['updated']

    def __getattr__(self, name):
        if self._modified:
            raise RuntimeError(self._class + ' has unsaved changes.')

        self._load()
        if name in self._columns:
            return self._get_column(name)
        if name in self._parents:
            return self._get_parent(name)
        if name in self._children:
            return self._get_children(name)
        if name in self._siblings:
            return self._get_siblings(name)
        raise AttributeError

    def __setattr__(self, name, value):
        if name in self._columns:
            self._set_column(name, value)
        elif name in self._parents:
            self._set_parent(name, value)
        else:
            super(Model, self).__setattr__(name, value)

    def _insert(self):
        columns = ', '.join(self._fields)
        placeholders = ', '.join(['%s'] * len(self._fields))

        query = self.__class__.insert_query.format(
            table=self._table,
            columns=columns,
            placeholders=placeholders
        )

        with self._cursor() as cursor:
            cursor.execute(query, list(self._fields.values()))
            self._id = cursor.fetchone()['id']

    def _load(self):
        if self._loaded:
            return

        query = self.__class__.select_query.format(table=self._table)

        with self._cursor() as cursor:
            cursor.execute(query, (self.id,))
            rows = cursor.fetchall()

        if len(rows) == 0:
            raise NotFoundError()

        for row in rows:
            self._fields = dict(row)
        self._loaded = True

    def _update(self):
        columns = ['{}=%s'.format(column) for column in self._fields]
        columns = ', '.join(columns)
        args    = list(self._fields.values()) + [self.id]
        query   = self.__class__.update_query.format(table=self._table,
                                                       columns=columns)

        with self._cursor() as cursor:
            cursor.execute(query, args)

    def _get_children(self, name):
        from db import models
        child_entity_name = self._children[name]
        child_table_name  = child_entity_name.lower()
        children = []
        cls = getattr(models, child_entity_name)
        query = self.__class__.parent_query.format(table=child_table_name,
                                                     parent=self._table)

        with self._cursor() as cursor:
            cursor.execute(query, (self.id,))
            rows = cursor.fetchall()

        for row in rows:
            child = self.__class__._row_to_instance(cls, row)
            children.append(child)
        return children

    def _get_column(self, name):
        return self._fields[name]

    def _set_column(self, name, value):
        self._modified = True
        self._fields[name] = value

    def _set_parent(self, name, value):
        self._modified = True
        if isinstance(value, Model):
            self._fields['{}_id'.format(name)] = value.id
        elif isinstance(value, int):
            self._fields['{}_id'.format(name)] = value
        else:
            self._modified = False
            raise AttributeError("Value must be instance of Model subclass or int")

    def delete(self):
        if self.id is None:
            message = 'Cannot delete an entity which has never been saved'
            raise RuntimeError(message)

        query = self.__class__.delete_query.format(table=self._table)
        with self._cursor() as cursor:
            cursor.execute(query, (self.id,))

        self._id = None
        self._loaded = False
        self._modified = False
        self._fields = {}

    def _get_parent(self, name):
        from db import models
        cls = getattr(models, name.title())
        query = self.__class__.select_query.format(table=name)
        key = '{}_id'.format(name)

        with self._cursor() as cursor:
            cursor.execute(query, (self._fields[key],))
            row = cursor.fetchone()

        return self.__class__._row_to_instance(cls, row)

    def _get_siblings(self, name):
        from db import models
        sibling_entity_name = self._siblings[name]
        sibling_table_name  = sibling_entity_name.lower()
        join_table_name = '__'.join(sorted([sibling_table_name, self._table]))

        query = self.__class__.sibling_query.format(
            table=self._table,
            sibling=sibling_table_name,
            join_table=join_table_name
        )

        cls = getattr(models, sibling_entity_name)

        with self._cursor() as cursor:
            cursor.execute(query, (self.id,))
            rows = cursor.fetchall()

        siblings = []
        for row in rows:
            instance = self.__class__._row_to_instance(cls, row)
            siblings.append(instance)
        return siblings

    @classmethod
    def all(cls):
        query  = cls.list_query.format(table=cls.__name__.lower())

        with get_cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
        instances = []
        for row in rows:
            instance = cls._row_to_instance(cls, row)
            instances.append(instance)

        return instances

    def save(self):
        if self.id is None:
            self._insert()
        else:
            self._update()

        self._modified = False

    @staticmethod
    def _row_to_instance(instance_class, row_data):
        instance = instance_class()
        instance._fields = dict(row_data)
        instance._id = row_data['id']
        instance._loaded = True

        return instance

