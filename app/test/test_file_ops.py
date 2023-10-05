
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
        
        assert "type" in resp.json()
        assert "version" in resp.json()
        assert "content" in resp.json()
        content = resp.json()["content"]
        assert isinstance(content, list)
        assert len(content) > 0

    for usfm_input in gospel_books_data:
        resp = client.put(f"{UNIT_URL}usfm/to/json?content_filter=paragraph",
            json=usfm_input)
        output = resp.json()
        assert "type" in output
        assert "content" in output

        # Iterate through the content to find chapters and verses
        found_chapter = False
        found_verse = False
        for content_item in output["content"]:
            if content_item.get("type") == "chapter:c":
                found_chapter = True
                assert "number" in content_item 
            elif content_item.get("type") == "verse:v":
                found_verse = True
                assert "number" in content_item 
                assert "sid" in content_item  
               
    # chapter filter
    resp = client.put(f"{UNIT_URL}usfm/to/json?chapter=10", json=gospel_books_data[0])
    output = resp.json()
    assert "book" in output

    # Check if 'book' has 'chapters' key and 'chapters' is an empty list for this particular chapter filter
    if 'chapters' in output['book']:
        assert len(output['book']['chapters']) == 0
    else:
        
        assert "book" in output
        assert "chapters" not in output['book']



def test_usfm_to_table():
    '''positive test to convert usfm to dict format'''
    for usfm_input in gospel_books_data:
        resp = client.put(f"{UNIT_URL}usfm/to/table", json=usfm_input)
        
        assert "Book\tChapter" in resp.json()
    for usfm_input in gospel_books_data:
        resp = client.put(f"{UNIT_URL}usfm/to/table?content_filter=paragraph",
            json=usfm_input)
        print("RESP.JSON",resp.json())
        assert "Book\tChapter\tVerse\tText\tType" in resp.json()
    
    
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

