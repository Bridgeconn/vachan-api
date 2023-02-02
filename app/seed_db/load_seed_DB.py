""" script for create and seed db for vachan engine """
import os
import csv
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

postgres_host = os.environ.get("VACHAN_POSTGRES_HOST", "localhost")
postgres_user = os.environ.get("VACHAN_POSTGRES_USER", "postgres")
postgres_database = os.environ.get("VACHAN_POSTGRES_DATABASE", "vachan")
postgres_password = os.environ.get("VACHAN_POSTGRES_PASSWORD", "secret")
postgres_port = os.environ.get("VACHAN_POSTGRES_PORT", "5432")
SEED_FILE = "seed_DB.sql"

current_dir = os.getcwd()

# key should be tableName and values is [] of file path in csvs dir
SEED_CSVS_NAMES_NO_FK = {
    "languages":{
        "columns":['language_code','language_name','script_direction','metadata'],
        "csvs":['consolidated_languages.csv']
        },
    "licenses":{
        "columns":['license_code', 'license_name', 'license_text', 'permissions'],
        "csvs":['licenses.csv']
        },
    "bible_books_look_up":{
        "columns":['book_id','book_name', 'book_code'],
        "csvs":['bible_books.csv']
        },
    "stopwords_look_up":{
        "columns":['language_id','stopword','confidence,created_user','last_updated_user','active'],
        "csvs":['stop_words/assamese.csv','stop_words/bengali.csv',
                'stop_words/gujarati.csv', 'stop_words/hindi.csv',
                'stop_words/kannada.csv', 'stop_words/malayalam.csv',
                'stop_words/marathi.csv', 'stop_words/punjabi.csv',
                'stop_words/tamil.csv', 'stop_words/telugu.csv' ]
        },
    "resource_types":{
        "columns":['resource_type_name','resource_type_description'],
        "csvs":['auth_resource_types.csv']
        },
    "permissions":{
        "columns":['permission_name'],
        "csvs":['auth_permissions.csv']
    }
}

#pylint: disable=use-dict-literal, broad-except, consider-using-f-string, W0621, E0702
APP_DICT = dict()
PERMISSION_DICT =dict()
RESOURCE_TYPE_DICT =dict()
APIPERMISSIONTABLE=[]
ACCESSRULESTABLE=[]

def db_real_dict_cursor_to_dict_with_custom_key(data, dict_key, headers_list):
    '''convert db realdictcursor data to dict with custom field as key'''
    output = dict()
    if data and dict_key and headers_list:
        headers = [x[0] for x in headers_list]
        if dict_key in headers:
            dict_key_indx = headers.index(dict_key)
            data_legth = len(data)
            header_legth = len(headers)
            # print(data_legth, header_legth)
            for i in range(data_legth):
                value_obj = dict()
                for j in range(header_legth):
                    value_obj[headers[j]] = data[i][j]
                output[data[i][dict_key_indx]] = value_obj
    return output

def update_csv_row_with_custom_fieldvalue_convert_to_tupple(csv_table, update_data):
    ''''update csv rows of table with custom field value and insert
        to DB. changing colum name should be a key in the Filed Dict
        * update data should containe 3 list with values csvColumnNum,
            Dict have that column name as key,
        and , dict value dict keyname for replace as in respective indexs
        return list of tuple to inser to DB'''
    csv_table_modified = []
    for row in csv_table:
        for indx, val in enumerate(update_data['columns']):
            # eg : value = APP_DICT[ key = name of row of column ][fieldName key value]
            fetch_db_dict = update_data['fieldDict'][indx]
            fetch_db_dict_key = row[val]
            fetch_db_dict_replace_key= update_data['fieldNames'][indx]
            # print(fetch_db_dict[fetch_db_dict_key][fetch_db_dict_replace_key])
            value = fetch_db_dict[fetch_db_dict_key][fetch_db_dict_replace_key]
            row[val] = value
        csv_table_modified.append(tuple(row))
    return csv_table_modified

def read_csv(path, output_list):
    '''read csv files'''
    with open(path,'r', encoding='utf-8') as file:
        csvreader = csv.reader(file)
        header = next(csvreader)#pylint: disable=unused-variable
        for table_row in csvreader:
            output_list.append(table_row)
        return output_list

#pylint: disable=inconsistent-return-statements
def create_db():
    """create db with psycopg2"""
    try:
        conn = psycopg2.connect(
        database="postgres",
        user=postgres_user,
        password=postgres_password,
        host=postgres_host,
        port= postgres_port
        )
        conn.autocommit = True
        cursor = conn.cursor()
        create_sql = ''' CREATE database %s '''% (postgres_database)
        cursor.execute(create_sql)
        conn.close()
        print("DB Created ------------")
        return True
    except Exception as err:
        print("db xxxxxxxxxxxxx : ", str(err))

def extract_and_execute_sql_file_qry(cursor,file_name):
    """sql file only contains query, no commnets or nothing"""
    try:
        with open(file_name,'r',encoding='utf-8') as file:
            sql_data = file.read().split(';')
            for query in sql_data:
                if len(query) > 0:
                    cursor.execute(query)
            print("All Tables created executed ----")
            return True
    except Exception as err:
        # print("Error on create tables from seed : ", err)
        raise err

def seed_data_to_created_tables_no_fk(cursor,conn, csv_dict):
    """seed data for the copy commands used in sql file"""
    try:
        for db_name, data_dict in csv_dict.items():
            for csv_name in data_dict["csvs"]:
                current_csv_data=[]
                current_csv_data = read_csv(os.path.join('csvs',csv_name), current_csv_data)
                current_csv_data = [tuple([None if x == '' else x for x in c]) for c in current_csv_data]
                csv_data_tuple = [tuple(l) for l in current_csv_data]
                keys_string = str.join(',', data_dict["columns"])
                insert_sql_cmd = f"INSERT INTO public.{db_name} ({keys_string}) VALUES %s"
                execute_values(cursor, insert_sql_cmd, csv_data_tuple)
                conn.commit()
                print(f"uploaded csv data for {db_name}")
        print("Finished upload csv to tables --------------------")
    except Exception as err:
        # print("Error in seed csv to dbs from dict : ", err)
        raise err

#pylint: disable=too-many-locals
def create_database_and_seed():
    """create and seed database"""
    try:
        # create database
        db_created = create_db()
        print('db exist value returned : ', db_created)
        if db_created:
            os.chdir(os.path.join(os.getcwd(),'seed_db'))
            # DB connection
            conn = psycopg2.connect(host=postgres_host, port=postgres_port,\
                dbname=postgres_database, user=postgres_user, password=postgres_password)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            # check db connection
            cursor.execute('SELECT 1')

            # extract query from seed sql and create tables without data
            extract_and_execute_sql_file_qry(cursor,SEED_FILE)

            # read csv and upload normal table data (data not needed foregin keys as id)
            seed_data_to_created_tables_no_fk(cursor,conn, SEED_CSVS_NAMES_NO_FK)

            # get all permissions in db
            qry = "SELECT * FROM public.permissions ORDER BY permission_id ASC "
            cursor.execute(query=qry)
            permissison_data = cursor.fetchall()
            permission_heads = cursor.description
            #pylint: disable=C0103
            PERMISSION_DICT= db_real_dict_cursor_to_dict_with_custom_key(permissison_data,\
                'permission_name', permission_heads)

            # get all resource types
            qry = "SELECT * FROM public.resource_types ORDER BY resource_type_id ASC "
            cursor.execute(query=qry)
            resource_type_data = cursor.fetchall()
            resource_type_heads = cursor.description
            #pylint: disable=C0103
            RESOURCE_TYPE_DICT= db_real_dict_cursor_to_dict_with_custom_key(resource_type_data,\
                'resource_type_name', resource_type_heads)

            #get all apps
            qry = "SELECT * FROM public.apps ORDER BY app_id ASC "
            cursor.execute(query=qry)
            app_data = cursor.fetchall()
            app_heads = cursor.description
            #pylint: disable=C0103
            APP_DICT= db_real_dict_cursor_to_dict_with_custom_key(app_data, 'app_name', app_heads)

            # Upload Access Rules CSV to DB with ID as FK
            read_csv('csvs/access_rules.csv', ACCESSRULESTABLE)
            update_access = {
                'columns':[0,1],
                'fieldDict':[RESOURCE_TYPE_DICT,PERMISSION_DICT],
                'fieldNames':['resource_type_id','permission_id'],
            }
            csv_table_modified_access = update_csv_row_with_custom_fieldvalue_convert_to_tupple\
                (ACCESSRULESTABLE, update_access)

            # insert converted tuple to DB
            insert_sql_access = "INSERT INTO public.access_rules \
                (entitlement_id, tag_id, roles) VALUES %s"
            execute_values(cursor, insert_sql_access, csv_table_modified_access)
            conn.commit()
            print("Uploaded Access Rule CSV to DB ====>")

            # Upload Permission Map CSV to DB with ID as FK
            read_csv('csvs/api_permissions.csv', APIPERMISSIONTABLE)
            update_map = {
                'columns':[2,4,5],
                'fieldDict':[APP_DICT,RESOURCE_TYPE_DICT,PERMISSION_DICT],
                'fieldNames':['app_id','resource_type_id','permission_id'],
            }
            csv_table_modified_permission_map = \
                update_csv_row_with_custom_fieldvalue_convert_to_tupple\
                (APIPERMISSIONTABLE, update_map)

            # insert converted tuple to DB
            insert_sql_map = "INSERT INTO public.api_permissions_map\
                (api_endpoint,method,request_app_id,filter_results,resource_type_id,permission_id) \
                    VALUES %s"
            execute_values(cursor, insert_sql_map, csv_table_modified_permission_map)
            conn.commit()
            print("Uploaded Api Permission Map CSV to DB ====>")
            conn.close()
        else:
            raise "seed db have error running"
    except Exception as err:
        print('error : ', err)
