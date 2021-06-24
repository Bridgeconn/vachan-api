'''GraphQL queries and mutations'''

import graphene

#pylint: disable=E0401
#pylint gives import error if relative import is not used. But app(uvicorn) doesn't accept it

from crud import structurals_crud, contents_crud, projects_crud, nlp_crud
from dependencies import get_db
from graphql_api import types, utils
