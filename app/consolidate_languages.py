'''An independant script not part of the webapp, used to create languages list for seed DB'''

import re
import json
import csv

key_val_pattern = re.compile(r'([\w-]+): (.+)\n')
leading_space_pattern = re.compile(r'^\s+')

#pylint: disable=too-many-branches, disable=too-many-statements, disable=too-many-locals

def read_language_subtag_registry(iana_file_path='../db/language-subtag-registry.txt'):
    '''converts data in text format to dict/json'''
    iana_data = {}
    iana_file = open(iana_file_path, 'r')
    new_obj = {}
    lines = iana_file.readlines()
    index = 0
    this_type = None
    while index < len(lines):
        line = lines[index]
        match_obj = re.match(key_val_pattern, line)
        if match_obj:
            key = match_obj.group(1)
            val = match_obj.group(2)
            if key == "Type":
                this_type = val
            if key in ["Comments", "Description"]:
                look_ahead = index + 1
                while look_ahead < len(lines):
                    next_line = lines[look_ahead]
                    if re.match(leading_space_pattern, next_line):
                        val += next_line
                    else:
                        index = look_ahead-1
                        break
                    look_ahead += 1
            if key not in new_obj:
                new_obj[key] = val
            else:
                old_val = new_obj[key]
                if not isinstance(old_val, list):
                    old_val = [old_val]
                new_obj[key] = old_val+[val]
        elif line.startswith("%") and bool(new_obj):
            if this_type not in iana_data:
                iana_data[this_type] = []
            iana_data[this_type].append(new_obj)
            new_obj = {}
        else:
            print("Unrecognized line:", line)
        index += 1
    return iana_data

def find_valid_codes(data):
    '''list all the valid codes for languages, scripts and regions'''
    valid_lang_codes = []
    valid_script_codes = []
    valid_region_codes = []
    valid_extended_langs = []
    valid_specific_variants = []
    valid_common_variants = []
    valid_grandpas = []
    valid_reduntants = []
    try:
        for item in data['language']:
            valid_lang_codes.append(item['Subtag'])
        for item in data['script']:
            valid_script_codes.append(item['Subtag'])
        for item in data['region']:
            valid_region_codes.append(item['Subtag'])
        for item in data['extlang']:
            valid_extended_langs.append(item['Prefix']+"-"+item['Subtag'])
        for item in data['variant']:
            if "Prefix" not in item or item["Prefix"] is None:
                valid_common_variants.append(item['Subtag'])
                continue
            if isinstance(item["Prefix"], str):
                item['Prefix'] = [item["Prefix"]]
            for pre in item['Prefix']:
                valid_specific_variants.append(pre+"-"+item["Subtag"])
        for item in data['grandfathered']:
            valid_grandpas.append(item["Tag"])
        for item in data['redundant']:
            valid_reduntants.append(item["Tag"])
    except Exception as exe:
        print("Error at :",item)
        raise exe
    valid_codes = {
        "primary_languages": valid_lang_codes,
        "scripts": valid_script_codes,
        "regions": valid_region_codes,
        "extlangs": valid_extended_langs,
        "variantSubtags": valid_common_variants,
        "variantsTags": valid_specific_variants,
        "grandfathered": valid_grandpas,
        'redundants': valid_reduntants
    }
    return valid_codes


def validate_language_code(lang_code, valid_codes):
    '''Validate input code against subtags in IANA subtag registry'''
    parts = lang_code.split("-")
    if parts[0].lower() in valid_codes['primary_languages']:
        parts.pop(0)
    if len(parts)> 0 and parts[0] in valid_codes['scripts']:
        parts.pop(0)
    if len(parts)> 0 and parts[0] in valid_codes['regions']:
        parts.pop(0)
    if len(parts)> 0 and parts[0] in valid_codes['variantSubtags']:
        parts.pop(0)
    full_matched = False
    if len(parts) > 0:
        if lang_code in valid_codes['extlangs']:
            full_matched = True
        if lang_code in valid_codes['variantsTags']:
            full_matched = True
        if lang_code in valid_codes['grandfathered']:
            full_matched = True
        if lang_code in valid_codes['redundants']:
            full_matched = True

    if len(parts) > 0 and not full_matched:
        raise Exception("Unrecognized subtags:"+str(parts)+" in "+ lang_code)
    return True

def process_language_subtag_registry(data):
    '''convert the data into table format importable to database and available in APIs'''
    # language fields: code, name, script_direction, similar_to,
    # metadata(region, description, use_instead, suppres-script)
    languages = []

    valid_codes = find_valid_codes(data)
    all_langs = data['language']+data['grandfathered']+data['redundant']+\
        data['extlang']+ data['variant']
    print("No of langs at first glance:", len(all_langs))
    code_count = 0
    for item in all_langs:
        try:
            codes = []
            if 'Prefix' in item:
                if item['Prefix'] is None:
                    continue
                if isinstance(item["Prefix"], list):
                    codes = [pre+"-" for pre in item['Prefix']]
                else:
                    codes = [item['Prefix']+'-']
            else:
                codes = ['']
            code_count += len(codes)
            if "Tag" in item:
                for i,code in enumerate(codes):
                    codes[i] = code + item['Tag']
            if "Subtag" in item:
                for i,code in enumerate(codes):
                    codes[i] = code + item['Subtag']
            desc = ""
            if "Deprecated" in item:
                desc += "Deprecated from "+ item["Deprecated"]+". "
            if "Scope" in item and item['Scope'] == "collection":
                desc += "This represents a collection of languages. "+\
                "Although a collection subtag can be used in the absence of a more specific tag,"+\
                " you should check whether a more specific language subtag is available. "
            if "Scope" in item and item['Scope'] == "macrolanguage":
                desc += "This represents a marco language. "+\
                "A more specific tag might be available. "
            if isinstance(item["Description"], list):
                name = item["Description"][0]
                desc += ". ".join(item["Description"][1:])
            else:
                name = item["Description"]
            metadata = {}
            similar_to = []
            if "Preferred-Value" in item:
                metadata['use-instead']: item['Preferred-Value']
                similar_to.append(item['Preferred-Value'])
            if "Macrolanguage" in item:
                metadata['macrolanguage'] = item['Macrolanguage']
                similar_to.append(item['Macrolanguage'])
            if "Comments" in item:
                desc += item['Comments']
            if "Suppress-Script" in item:
                metadata['suppress-script'] = item['Suppress-Script']
            if desc != "":
                metadata['description'] = desc
            for code in codes:
                if validate_language_code(code, valid_codes):
                    languages.append({"code":code, "name":name, "script-direction":None,
                        "similar_to":similar_to, "metadata": metadata})
        except Exception as exe:
            print("Error at:", item)
            raise exe
    return languages

def add_from_trans_database_to_languages(languages_list, registry_data,
    json_filepath='../db/langnames_from_translationDatabase.json'):
    '''collect languages from unfoldngword's translation database and add to our list'''
    languages_dict = {lang["code"]:lang for lang in languages_list}

    loaded_json = json.loads(open(json_filepath, "r").read())
    for lang in loaded_json:
        code = lang['lc']
        country_code = lang['hc']
        country = None
        for reg in registry_data['region']:
            if reg['Subtag'] == country_code:
                if isinstance(reg['Description'], list):
                    country = ", ".join(reg['Description'])
                else:
                    country = reg['Description']
                break
        if lang['ang'] != "":
            name = lang['ang']
        else:
            name = lang['ln']
        new_info = {
            "code":lang['lc'],
            "name":name,
            "script-direction": lang['ld'],
            "metadata":{}
        }
        region = []
        if country is not None:
            region.append(country)
        if lang['lr'] != "":
            region.append(lang['lr'])
        if len(region) > 0:
            new_info["metadata"]['region'] =  ", ".join(region)
        if len(lang['alt']) > 0:
            new_info["metadata"]['alternate-names']= lang['alt']
        if lang['gw']:
            new_info["metadata"]['is-gateway-language']= lang['gw']

        if code in languages_dict:
            known_info = languages_dict[code]
            known_info["script-direction"] = new_info['script-direction']
            if "region" in new_info['metadata']:
                known_info['metadata']['region'] = new_info['metadata']['region']
            if "alternate-names" in new_info['metadata']:
                known_info['metadata']['alternate-names'] = new_info['metadata']['alternate-names']
            if "is-gateway-language" in new_info['metadata']:
                known_info['metadata']["is-gateway-language"] = \
                    new_info['metadata']['is-gateway-language']
            languages_dict[code] = known_info
        else:
            languages_dict[code] = new_info
    new_list = [ languages_dict[key] for key in languages_dict]
    return new_list

def add_from_venea_list(languages_list, venea_filepath='../db/languages-venea.tsv'):
    '''read the langauges from the TSV file and append them to common pool'''
    languages_dict = {lang["code"]:lang for lang in languages_list}

    with open(venea_filepath, newline='') as csvfile:
        lang_reader = csv.reader(csvfile, delimiter='\t')
        next(lang_reader, None) #skip header
        for row in lang_reader:
            name = row[0].strip()
            code = row[4].strip()
            if code not in languages_dict:
                languages_dict[code] = {"code":code, "name":name}
    new_list = [ languages_dict[key] for key in languages_dict]
    return new_list

def write_to_csv(languages_list):
    '''Save the consolidated list to a csv file to be imported to DB later'''
    with open('../db/consolidated_languages.csv', 'w', newline='') as csvfile:
        lang_writer = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for lang in languages_list:
            if lang['code'] is None or lang['code'] == "":
                # print("No code:",lang)
                continue
            row = [lang['code'], lang['name']]
            if "script-direction" in lang:
                row.append(lang['script-direction'])
            else:
                row.append(None)
            if "metadata" in lang:
                meta_str = json.dumps(lang['metadata'])
                row.append(meta_str)
            else:
                row.append(None)

            lang_writer.writerow(row)

if __name__ == '__main__':
    content = read_language_subtag_registry()
    langs = process_language_subtag_registry(content)
    print("languages from IANA:", len(langs))
    updated_langs = add_from_trans_database_to_languages(langs, content)
    print("after appending languages from translation database:", len(updated_langs))
    final_list = add_from_venea_list(updated_langs)
    print("final list length:",len(final_list))
    write_to_csv(final_list)
