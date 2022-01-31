'''defines the graphql router'''
from fastapi import APIRouter, Depends, BackgroundTasks
import graphene
from starlette.requests import Request
from starlette.graphql import GraphQLApp
from graphql.execution.executors.asyncio import AsyncioExecutor

from graphql_api import queries, mutations
from dependencies import get_db

router = APIRouter()

schema=graphene.Schema(query=queries.Query,mutation=mutations.VachanMutations)
graphql_app = GraphQLApp(schema , executor_class=AsyncioExecutor)

@router.post('/graphql')
async def single_endpoint(request: Request, background_tasks : BackgroundTasks,
    db_session=Depends(get_db)):
    '''One endpoint for all graphql operations'''
    request.db_session = db_session
    request.background_tasks = background_tasks
    return await graphql_app.handle_graphql(request=request)

@router.get('/graphql')
async def graphiql(request: Request, background_tasks : BackgroundTasks,
    db_session=Depends(get_db)):
    '''Get endpoint for graphiQL interface'''
    request.db_session = db_session
    request.background_tasks = background_tasks
    return await graphql_app.handle_graphql(request=request)
