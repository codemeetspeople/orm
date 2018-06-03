import yaml
from copy import deepcopy
import config
import os


class table:
    __tablename__ = None
    __m2m__ = False

    def _init_defaults(self):
        if self.__m2m__:
            return

        self.id = 'serial primary key'
        self.created = 'timestamp NOT NULL DEFAULT now()'
        self.updated = 'timestamp NULL'

        self._fields = []
        self._parents = []
        self._children = {}
        self._siblings = {}

    def __init__(self):
        self._init_defaults()

    def update_fields(self, fields):
        for f_title, f_type in fields.items():
            setattr(self, f_title, f_type)

    @property
    def fields(self):
        fields_list = []

        for f_title, f_type in self.__dict__.items():
            if f_title.startswith('_'):
                continue

            fields_list.append(f'  {f_title} {f_type}')
        return fields_list

    def to_sql(self):
        return (
            'DROP TABLE IF EXISTS "{table}" CASCADE;\n'
            'CREATE TABLE "{table}"'
            '(\n{fields}\n);\n'
        ).format(
            table=self.__tablename__,
            fields=',\n'.join(self.fields)
        )

    def to_python(self):
        columns = ', '.join(map(lambda x: '\'{}\''.format(x), self._fields))
        parents = ', '.join(map(lambda x: '\'{}\''.format(x), self._parents))
        children = ', '.join(['\'{}\': \'{}\''.format(k, v) for k, v in self._children.items()])
        siblings = ', '.join(['\'{}\': \'{}\''.format(k, v) for k, v in self._siblings.items()])

        return (
            'class {classname}(Model):\n'
            '    _columns = [{columns}]\n'
            '    _parents = [{parents}]\n'
            '    _children = {{{children}}}\n'
            '    _siblings = {{{siblings}}}\n'
        ).format(
            classname=self.__class__.__name__,
            columns=columns,
            parents=parents,
            children=children,
            siblings=siblings
        )


class SQLGenerator:
    def __init__(self):
        self.schema_path = os.path.join(config.DB_SOURCE_DIR, 'schema.yaml')
        self._tables = {}
        self._alters = []

        self._read_schema()

    def _read_schema(self):
        with open(self.schema_path, 'r') as f:
            self._data = yaml.load(f.read())

    def _table(self, name, fields, m2m=False):
        tbl_name = name.lower()
        if m2m:
            name = ''.join([n.capitalize() for n in name.split('__')])
        tbl = type(name, (table,), {})
        tbl.__tablename__ = tbl_name
        tbl.__m2m__ = m2m
        tbl_obj = tbl()
        tbl_obj.update_fields(fields)
        if not m2m:
            tbl_obj._fields += fields.keys()
        self._tables[name] = tbl_obj

    def _create_tables(self):
        for table_name, data in self._data.items():
            self._table(table_name, data.get('fields', {}))

    def _create_m2m_fk(self, m2m_table, t1, t2):
        fk_name = ''.join(m2m_table.split('__'))
        return (
            f'ALTER TABLE "{m2m_table}"'
            f' ADD CONSTRAINT "fk_{fk_name}_{t1}_id"'
            f' FOREIGN KEY ("{t1}_id") REFERENCES "{t1}"("id");'
        )

    def _create_fk(self, parent, child):
        return (
            f'ALTER TABLE "{child}"'
            f' ADD CONSTRAINT "fk_{child}_{parent}_id"'
            f' FOREIGN KEY ("{parent}_id") REFERENCES "{parent}"("id");'
        )

    def _create_m2m(self, parent, child, data):
        parent_table = parent.lower()
        child_table = child.lower()

        fields = dict([
            (f'{parent_table}_id', 'bigint not null'),
            (f'{child_table}_id', 'bigint not null'),
        ])

        table_name = f'{parent_table}__{child_table}'
        self._table(table_name, fields, m2m=True)

        self._alters.extend([
            self._create_m2m_fk(table_name, parent_table, child_table),
            self._create_m2m_fk(table_name, child_table, parent_table),
        ])

        self._tables[child]._siblings[parent_table] = parent
        self._tables[parent]._siblings[child_table] = child

        del data[child]['relations'][parent]

    def _create_o2m(self, parent, child):
        parent_table = parent.lower()
        child_table = child.lower()

        setattr(self._tables[child], f'{parent_table}_id', 'bigint not null')
        self._alters.append(self._create_fk(parent_table, child_table))

        self._tables[parent]._children[child_table] = child
        self._tables[child]._parents.append(parent_table)

    def _process_relations(self):
        schema = deepcopy(self._data)

        for parent, data in schema.items():
            for child, relation in data.get('relations', {}).items():
                if relation == 'many' and schema[child]['relations'][parent] == 'many':
                    self._create_m2m(parent, child, schema)
                
                if relation == 'one' and schema[child]['relations'][parent] == 'many':
                    self._create_o2m(child, parent)
                
    def generate(self):
        self._create_tables()
        self._process_relations()

        sql_dump = (
            '{}\n\n{}\n'.format(
                '\n'.join([t.to_sql() for t in self._tables.values()]),
                '\n\n'.join(self._alters)
            )
        )

        with open(os.path.join(config.DB_SOURCE_DIR, 'db.sql'), 'w') as f:
            f.write(sql_dump)

        with open(os.path.join(config.DB_DIR, 'models.py'), 'w') as f:
            f.write((
                'from db.base import Model\n\n\n'
                '{}'
            ).format('\n\n'.join([t.to_python() for t in self._tables.values() if not t.__m2m__])))
