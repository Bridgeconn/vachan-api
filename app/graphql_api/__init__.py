'''defines the graphql router'''
from fastapi import APIRouter, Depends
import graphene
from starlette.requests import Request
from starlette.graphql import GraphQLApp

#pylint: disable=E0401
#pylint gives import error if relative import is not used. But app(uvicorn) doesn't accept it
from graphql_api import queries, mutations
from dependencies import get_db

router = APIRouter()

schema=graphene.Schema(query=queries.Query,mutation=mutations.VachanMutations)
graphql_app = GraphQLApp(schema)

@router.post('/graphql')
async def single_endpoint(request: Request, db_session=Depends(get_db)):
    '''One endpoint for all graphql operations'''
    request.db_session = db_session
    return await graphql_app.handle_graphql(request=request)

@router.get('/graphql')
async def graphiql(request: Request, db_session=Depends(get_db)):
    '''Get endpoint for graphiQL interface'''
    request.db_session = db_session
    return await graphql_app.handle_graphql(request=request)
