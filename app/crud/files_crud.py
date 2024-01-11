'''Place to define all file handing and format conversion logics'''
#pylint: disable=C0303,W0311, I1101
import usfm_grammar
from lxml import etree
from usfm_grammar import USFMParser, Filter

def extract_dict_chapter(converted_content:dict, chapter:int):
    output_content = {
        "type": "USJ",
        "version": "0.1.0",
        "content": []
    }
    
    # Initialize a flag to check if the chapter is found
    chapter_found = False
    
    for item in converted_content["content"]:
        if item["type"] == "book:id":
            output_content["content"].append(item)
        elif item["type"] == "chapter:c" and item.get("number") == str(chapter):
            # Add the chapter and set the flag to True
            output_content["content"].append(item)
            chapter_found = True
        elif item["type"] == "para:p" and chapter_found:
            # Add para:p elements after the chapter is found
            output_content["content"].append(item)
    
    return output_content




def extract_list_chapter(converted_content: list, chapter:int) -> list:
    '''Extract the rows of specified chapter from usfm-grammar's list output'''
    output_content = [converted_content[0]]
    for row in converted_content[1:]:
        if int(row[1]) == chapter:
            output_content.append(row)
    return output_content

def extract_usx_chapter(converted_content, chapter:int):
    '''Extract one chapter from USX file'''
    output_content = etree.Element("usx") #pylint: disable=I1101
    for attr in converted_content.keys():
        output_content.set(attr, converted_content.get(attr))
    in_correct_chapter = False
    in_other_chapter = False
    for child in converted_content:
        if child.tag != 'chapter' and not in_correct_chapter and not in_other_chapter:
            output_content.append(child)
        elif child.tag != 'chapter' and in_correct_chapter and not in_other_chapter:
            output_content.append(child)
        elif child.tag != 'chapter' and not in_correct_chapter and in_other_chapter:
            ...
        elif child.tag == "chapter":
            if 'sid' in child.keys():
                if int(child.get('sid').split(" ")[-1]) == int(chapter):
                    output_content.append(child)
                    in_correct_chapter = True
                else:
                    in_other_chapter = True
            else:
                if in_correct_chapter:
                    output_content.append(child)
                in_correct_chapter = False
                in_other_chapter = False
    return output_content






def parse_with_usfm_grammar(input_usfm, output_format=usfm_grammar.Format.JSON,chapter=None,#pylint: disable= R0912, R0915
                             include_markers=None, exclude_markers=None):
    usfm_parser = USFMParser(input_usfm)
    included_markers = []
    excluded_markers = []
    if include_markers:
        if "PARAGRAPHS" in include_markers:
            included_markers.extend(Filter.PARAGRAPHS.value)
        # Check if "BCV" is present in include_markers
        if "BCV" in include_markers:
            included_markers.extend(Filter.BCV.value)
        if "COMMENTS" in include_markers:
            included_markers.extend(Filter.COMMENTS.value)
        if "TITLES" in include_markers:
            included_markers.extend(Filter.TITLES.value)
        if "BOOK_HEADERS" in include_markers:
            included_markers.extend(Filter.BOOK_HEADERS.value)       
        if "TEXT" in include_markers:
            included_markers.extend(Filter.TEXT.value)
        if "NOTES" in include_markers:
            included_markers.extend(Filter.NOTES.value)
        if "STUDY_BIBLE" in include_markers:
            included_markers.extend(Filter.STUDY_BIBLE.value)

        else:
            for marker in include_markers:
                if marker in Filter.PARAGRAPHS.value:
                        included_markers.append(marker)
                if marker in Filter.BCV.value:
                    included_markers.append(marker)
                if marker in Filter.COMMENTS.value:
                    included_markers.append(marker)
                if marker in Filter.TITLES.value:
                    included_markers.append(marker)
                if marker in Filter.CHARACTERS.value:
                    included_markers.append(marker)
                if marker in Filter.BOOK_HEADERS.value:
                    included_markers.append(marker)
                if marker in Filter.TEXT.value:
                    included_markers.append(marker)
                if marker in Filter.NOTES.value:
                    included_markers.append(marker)
                if marker in Filter.STUDY_BIBLE.value:
                    included_markers.append(marker)
    if exclude_markers:
        # Check if any of the exclude_markers match with Filter.PARAGRAPHS
        if "PARAGRAPHS" in exclude_markers:
            # If "PARAGRAPHS" is present, exclude all markers in Filter.PARAGRAPHS
            excluded_markers.extend(Filter.PARAGRAPHS.value)
        if "BCV" in exclude_markers:
            excluded_markers.extend(Filter.BCV.value)
        if "COMMENTS" in exclude_markers:
            excluded_markers.extend(Filter.COMMENTS.value)
        if "TITLES" in exclude_markers:
            excluded_markers.extend(Filter.TITLES.value)
        if "BOOK_HEADERS" in exclude_markers:
            excluded_markers.extend(Filter.BOOK_HEADERS.value)
        if "NOTES" in exclude_markers:
            excluded_markers.extend(Filter.NOTES.value)
        if "STUDY_BIBLE" in exclude_markers:
            excluded_markers.extend(Filter.STUDY_BIBLE.value)
        else:
            for marker in exclude_markers:               
                if marker in Filter.PARAGRAPHS.value:
                    excluded_markers.append(marker)
                if marker in Filter.BCV.value:
                    excluded_markers.append(marker)
                if marker in Filter.COMMENTS.value:
                    excluded_markers.append(marker)
                if marker in Filter.TITLES.value:
                    excluded_markers.append(marker)
                if marker in Filter.CHARACTERS.value:
                    excluded_markers.append(marker)
                if marker in Filter.BOOK_HEADERS.value:
                    excluded_markers.append(marker)
                if marker in Filter.NOTES.value:
                    excluded_markers.append(marker)
                if marker in Filter.STUDY_BIBLE.value:
                    excluded_markers.append(marker)
    output_content = None
    match output_format:
        case usfm_grammar.Format.JSON:
            output_content = usfm_parser.to_usj( )
            if excluded_markers:
                output_content = usfm_parser.to_usj(exclude_markers=excluded_markers)
            elif included_markers:
                output_content = usfm_parser.to_usj(include_markers=included_markers)
            # else:
            if chapter is not None:
                output_content = extract_dict_chapter(output_content, chapter)
        case usfm_grammar.Format.CSV:
            output_content = usfm_parser.to_list( )
            if excluded_markers:
                output_content = usfm_parser.to_usj(exclude_markers=excluded_markers)
            elif included_markers:
                output_content = usfm_parser.to_usj(include_markers=included_markers)
            # else:
            if chapter is not None:
                output_content = extract_list_chapter(output_content, chapter)
            output_content = "\n".join(['\t'.join(list(row)) for row in output_content])
        case usfm_grammar.Format.ST:
            output_content = usfm_parser.to_syntax_tree()
            # if chapter is not None:
        case usfm_grammar.Format.USX:
            output_content = usfm_parser.to_usx()
            if chapter is not None:
                output_content = extract_usx_chapter(output_content, chapter)
            output_content = etree.tostring(output_content, encoding='unicode', pretty_print=True)

    return output_content
