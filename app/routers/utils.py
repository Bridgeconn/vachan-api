# pylint: disable=R0801
'''Utility functions'''
from dependencies import log
from schema import schema_auth
from routers.content_apis import get_source

async def get_source_and_permission_check(source_name, request, user_details, db_):
    """get source with acess right check"""
    # check getting source
    parts = source_name.split('_')
    language_code = parts[0]
    version_abbreviation = parts[1]
    revision = parts[2]
    content_type = parts[3]
    try:
        tables = await get_source(request=request, content_type=content_type,
        version_abbreviation=version_abbreviation,
        revision=revision,language_code=language_code,license_code=None,
        metadata=None,access_tag = None, active= True, latest_revision= True,
        skip=0, limit=1000, user_details=user_details, db_=db_,
        operates_on=schema_auth.ResourceType.CONTENT.value,
        filtering_required=True)
        return tables
    except Exception:
        log.error("Error in getting sources list")
        raise
