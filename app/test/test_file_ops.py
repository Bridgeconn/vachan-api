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
        # print("Response:", resp.json())  # Add this line to print the response
        assert "content" in resp.json()

        # Assert book:id
        found_book_id = False
        for content in resp.json()["content"]:
            if content.get("type") == "book:id" and content.get("code"):
                found_book_id = True
                print("Book ID:", content.get("code"))
                assert "code" in content

        # Assert chapter:c
        found_chapter = False
        for content in resp.json()["content"]:
            if content.get("type") == "chapter:c" and content.get("number"):
                found_chapter = True
                print("Chapter Number:", content.get("number"))
                assert "number" in content
                assert "sid" in content

        # Assert the presence of chapter:c
        assert found_chapter

        # Assert para:p and verse:v
        found_para = False
        found_verse = False

        for content in resp.json()["content"]:
            if isinstance(content, dict):
                if content.get("type") == "para:p":
                    found_para = True
                    for content_item in content.get("content", []):
                        if (
                            isinstance(content_item, dict)
                            and content_item.get("type") == "verse:v"
                        ):
                            found_verse = True
                            assert "number" in content_item
                            print("Verse Number:", content_item["number"])
                            assert "sid" in content_item
                            # Add additional assertions for verse content as needed

        # Assert the presence of para:p and verse:v
        assert found_para
        assert found_verse
                       


               

    for usfm_input in gospel_books_data:
        resp = client.put(f"{UNIT_URL}usfm/to/json?include_markers=BCV", json=usfm_input)
        # print("Response:", resp.json())  # Add this line to print the response
        assert "content" in resp.json()

        # Assert book:id
        found_book_id = any(
            content.get("type") == "book:id" and content.get("code")
            for content in resp.json()["content"]
        )
        assert found_book_id

        # Assert chapter:c
        found_chapter = any(
            content.get("type") == "chapter:c" and content.get("number")
            for content in resp.json()["content"]
        )
        assert found_chapter

        # Assert not  para:p
        found_para = any(
            content.get("type") == "para:p" for content in resp.json()["content"]
        )
        assert not found_para

        # Assert verse:v
        found_verse = any(
            content.get("type") == "verse:v" for content in resp.json()["content"]
        )
        assert  found_verse



    for usfm_input in gospel_books_data:
        resp = client.put(f"{UNIT_URL}usfm/to/json?exclude_markers=v", json=usfm_input)
        # print("Response:", resp.json())  # Add this line to print the response
        assert "content" in resp.json()

        # Assert book:id
        found_book_id = any(
            content.get("type") == "book:id" and content.get("code")
            for content in resp.json()["content"]
        )
        assert found_book_id, "No book:id found"

        # Assert chapter:c
        found_chapter = any(
            content.get("type") == "chapter:c" and content.get("number")
            for content in resp.json()["content"]
        )
        assert found_chapter, "No chapter:c found"

        # Assert para:p
        found_para = any(
            content.get("type") == "para:p" for content in resp.json()["content"]
        )
        assert found_para, "No para:p found"

        # Assert verse:v
        found_verse = any(
            content.get("type") == "verse:v" for content in resp.json()["content"]
        )
        assert not found_verse, "Verse:v found unexpectedly"

    
    
    
    # chapter filter
    resp = client.put(f"{UNIT_URL}usfm/to/json?chapter=10", json=gospel_books_data[0])
    assert "content" in resp.json()
    chapter_numbers = [
        content.get("number")
        for content in resp.json()["content"]
        if content.get("type") == "chapter:c"
    ]
    assert len(chapter_numbers) == 0, f"Expected 0 chapters, but found {len(chapter_numbers)}"



    
    
    resp = client.put(f"{UNIT_URL}usfm/to/json?chapter=2", json=gospel_books_data[0])
    print("Response:", resp.json())  # Add this line to print the response
    assert "content" in resp.json()
    # Assert chapter:c
    chapter_numbers = [
        content.get("number")
        for content in resp.json()["content"]
        if content.get("type") == "chapter:c"
    ]
    assert len(chapter_numbers) == 1, f"Expected 1 chapter, but found {len(chapter_numbers)}"
    assert "2" in chapter_numbers




def test_usfm_to_table():
    '''positive test to convert usfm to dict format'''
    for usfm_input in gospel_books_data:
        resp = client.put(f"{UNIT_URL}usfm/to/table", json=usfm_input)
        assert "Book\tChapter" in resp.json()
    for usfm_input in gospel_books_data:
        resp = client.put(f"{UNIT_URL}usfm/to/table?include_markers=BCV",
            json=usfm_input)
        assert "t\ty\tp\te\nv" in resp.json()
    
    
    for usfm_input in gospel_books_data:
        resp = client.put(f"{UNIT_URL}usfm/to/table?exclude_markers=p",
            json=usfm_input)
        assert "t\ty\tp\te\nv" in resp.json()
    
    
    # chapter filter
    resp = client.put(f"{UNIT_URL}usfm/to/table?chapter=2",
        json=gospel_books_data[0])
    assert "MAT\t2" in resp.json() 
    assert "MAT\t1" not in resp.json()

def test_usfm_to_usx():
    '''positive test to convert usfm to dict format'''
    for usfm_input in gospel_books_data:
        resp = client.put(f"{UNIT_URL}usfm/to/usx", json=usfm_input)
        print(resp.json())
        assert resp.json().startswith("<usx")
        assert resp.json().strip().endswith("</usx>")
