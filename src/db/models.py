from db.base import Model


class Article(Model):
    _columns = ['title', 'text']
    _parents = ['category']
    _children = {}
    _siblings = {'tag': 'Tag'}


class Category(Model):
    _columns = ['title']
    _parents = []
    _children = {'article': 'Article'}
    _siblings = {}


class Tag(Model):
    _columns = ['value']
    _parents = []
    _children = {}
    _siblings = {'article': 'Article'}
