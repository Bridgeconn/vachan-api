'''Place to define all file handing and format conversion logics'''

import usfm_grammar
from lxml import etree
from dependencies import log

def extract_dict_chapter(converted_content:dict, chapter:int) -> dict:
    '''Extracts just one chapter from the dict or JSON of usfm grammar'''
    output_content = {"book":{}}
    for item in converted_content['book']:
        if item != 'chapters':
            output_content['book'][item] = converted_content['book'][item]
        else:
            output_content['book']['chapters'] = []
            for chapter_dict in converted_content['book']['chapters']:
                if int(chapter_dict['chapterNumber']) == chapter:
                    output_content['book']['chapters'].append(chapter_dict)
                    break
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

def parse_with_usfm_grammar(input_usfm, output_format=usfm_grammar.Format.JSON,
    content_filter=usfm_grammar.Filter.SCRIPTURE_PARAGRAPHS,
    chapter=None):
    '''Tries to parse the input usfm and provide the output as per the filter and format'''
    usfm_parser = usfm_grammar.USFMParser(input_usfm)
    match output_format:
        case usfm_grammar.Format.JSON:
            output_content = usfm_parser.to_dict(content_filter)
            if chapter is not None:
                output_content = extract_dict_chapter(output_content, chapter)
        case usfm_grammar.Format.CSV:
            output_content = usfm_parser.to_list(content_filter)
            if chapter is not None:
                output_content = extract_list_chapter(output_content, chapter)
            output_content = "\n".join(['\t'.join(list(row)) for row in output_content])
        case usfm_grammar.Format.ST:
            output_content = usfm_parser.to_syntax_tree()
            if chapter is not None:
                log.warning("Not implemented chapter extracter for syntax_tree")
        case usfm_grammar.Format.USX:
            output_content = usfm_parser.to_usx(content_filter)
            if chapter is not None:
                output_content = extract_usx_chapter(output_content, chapter)
            output_content = etree.tostring(output_content, encoding='unicode', pretty_print=True) #pylint: disable=I1101
    return output_content
