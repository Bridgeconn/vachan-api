''' tests for file manipulation APIs'''

from . import client
from . import assert_input_validation_error, assert_not_available_content

from .conftest import initial_test_users


UNIT_URL = "/v2/files/"

gospel_books_data = [
        {"USFM":"\\id MAT\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"+\
            "\n\\c 2\n\\p\n\\v 1 test verse three\n\\v 2 test verse four"},
        {"USFM":"\\id MRK\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
        {"USFM":"\\id LUK\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
        {"USFM":"\\id JHN\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"}
]


def test_usfm_to_json():
    '''positive test to convert usfm to dict format'''
    for usfm_input in gospel_books_data:
        resp = client.put(f"{UNIT_URL}usfm/to/json", json=usfm_input)
        assert "book" in resp.json()
        assert "chapters" in resp.json()['book']

    for usfm_input in gospel_books_data:
        resp = client.put(f"{UNIT_URL}usfm/to/json?content_filter=scripture-bcv",
            json=usfm_input)
        output = resp.json()
        assert "book" in output
        assert "chapters" in output['book']
        assert output['book']['chapters'][0]['chapterNumber']
        found_verse = False
        for content in output['book']['chapters'][0]['contents']:
            if "verseNumber" in content and "verseText" in content:
                found_verse = True
                break
        assert found_verse

    for usfm_input in gospel_books_data:
        resp = client.put(f"{UNIT_URL}usfm/to/json?content_filter=scripture-paragraph",
            json=usfm_input)
        output = resp.json()
        assert "book" in output
        assert "chapters" in output['book']
        assert output['book']['chapters'][0]['chapterNumber']
        found_para = False
        found_verse = False
        for content in output['book']['chapters'][0]['contents']:
            if "paragraph" in content:
                found_para = True
                for item in content['paragraph']:
                    if "verseNumber" in item:
                        found_verse = True
                        break
        assert found_para
        assert found_verse

    # chapter filter
    resp = client.put(f"{UNIT_URL}usfm/to/json?chapter=10",
        json=gospel_books_data[0])
    output = resp.json()
    assert "book" in output
    assert "chapters" in output['book']
    assert len(output['book']['chapters']) == 0

    resp = client.put(f"{UNIT_URL}usfm/to/json?chapter=2",
        json=gospel_books_data[0])
    output = resp.json()
    assert "book" in output
    assert "chapters" in output['book']
    assert len(output['book']['chapters']) == 1
    assert int(output['book']['chapters'][0]['chapterNumber']) == 2


def test_usfm_to_table():
    '''positive test to convert usfm to dict format'''
    for usfm_input in gospel_books_data:
        resp = client.put(f"{UNIT_URL}usfm/to/table", json=usfm_input)
        assert "Book\tChapter" in resp.json()
    for usfm_input in gospel_books_data:
        resp = client.put(f"{UNIT_URL}usfm/to/table?content_filter=scripture-paragraph",
            json=usfm_input)
        assert "Book\tChapter\tType\tContent" in resp.json()
    for usfm_input in gospel_books_data:
        resp = client.put(f"{UNIT_URL}usfm/to/table?content_filter=scripture-bcv",
            json=usfm_input)
        assert "Book\tChapter\tVerse\tText" in resp.json()
    
    # chapter filter
    resp = client.put(f"{UNIT_URL}usfm/to/table?chapter=2",
        json=gospel_books_data[0])
    output = resp.json()
    assert "MAT\t2" in output 
    assert "MAT\t1" not in output

def test_usfm_to_usx():
    '''positive test to convert usfm to dict format'''
    for usfm_input in gospel_books_data:
        resp = client.put(f"{UNIT_URL}usfm/to/usx", json=usfm_input)
        print(resp.json())
        assert resp.json().startswith("<usx")
        assert resp.json().strip().endswith("</usx>")


