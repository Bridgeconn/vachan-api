'''Test cases for media related APIs'''
from . import client
from .test_versions import check_post as add_version
from .test_sources import check_post as add_source
from .test_auth_basic import login,SUPER_USER,SUPER_PASSWORD,logout_user
from .conftest import initial_test_users

UNIT_URL = '/v2/media/gitlab'
# REPO_PERMANENT_LINK = "https://gitlab.bridgeconn.com/Test.User/trial-media-project/-/blob/main/large videos/graphql.mp4"
REPO_PERMANENT_LINK = "https://gitlab.bridgeconn.com/Siju.Moncy/trial-media-project/-/blob/main/large videos/graphql.mp4"

headers = {"contentType": "application/json", "accept": "application/json"}


def media_common(endpoint,permanent_link, repo, file_path):
    '''test for media download endpoint'''
    # test without source of repo in metadata
    response = client.get(UNIT_URL+endpoint+"?permanent_link="+permanent_link, headers=headers)
    assert response.status_code == 404
    assert response.json()["error"] == "Requested Content Not Available"

    # Create Source with repo link for gitlab media
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version for Gitlab",
    }
    add_version(version_data)
    source_data = {
        "contentType": "gitlabrepo",
        "language": "en",
        "version": "TTT",
        "revision": 1,
        "year": 2000,
        "license": "ISC",
        "metaData": {"repo": permanent_link.split("/-/")[0]}
    }
    source = add_source(source_data)
    source_name = source.json()['data']['sourceName']

    # Source with access permission content , need higher auth level to access
    # Without auth
    response = client.get(UNIT_URL+"/download"+"?permanent_link="+REPO_PERMANENT_LINK, headers=headers)
    assert response.status_code == 404
    assert response.json()["error"] == "Requested Content Not Available"

    # with auth . Normal Registered User NO access to content
    response = client.get(UNIT_URL+"/download"+"?permanent_link="+REPO_PERMANENT_LINK+
        "&access_token="+initial_test_users['APIUser']['token'])
    assert response.status_code == 404
    assert response.json()["error"] == "Requested Content Not Available"

    # Not providing permanent link or repo data
    response = client.get(UNIT_URL+"/download"+"?access_token="+initial_test_users['VachanAdmin']['token'])
    assert response.status_code == 422
    assert response.json()["error"] == "Unprocessable Data"

    # stream only support audio and video
    if endpoint == "/stream":
        jpg_link = "https://gitlab.bridgeconn.com/Siju.Moncy/trial-media-project/-/blob/main/image/Bible_Timeline.jpg"
        response = response = client.get(UNIT_URL+"/stream"+"?permanent_link="+jpg_link+
        "&access_token="+initial_test_users['VachanAdmin']['token'])
        assert response.status_code == 406
        assert response.json()["details"] == 'Currently api supports only video and audio streams'

        # range header not present in request (request not from a player)
        response = client.get(UNIT_URL+"/stream"+"?permanent_link="+REPO_PERMANENT_LINK+
        "&access_token="+initial_test_users['VachanAdmin']['token'])
        assert response.status_code == 406
        assert response.json()["details"] ==\
            'This is a Streaming api , Call it from supported players'

def test_media_download_checks():
    """checks for download api"""
    media_common("/download",REPO_PERMANENT_LINK,
        "https://gitlab.bridgeconn.com/Siju.Moncy/trial-media-project", "large videos/graphql.mp4")

def test_media_stream_checks():
    """checks for download api"""
    media_common("/stream", REPO_PERMANENT_LINK,
        "https://gitlab.bridgeconn.com/Siju.Moncy/trial-media-project", "large videos/graphql.mp4")
