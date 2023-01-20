import os
import psycopg2
from psycopg2.extras import execute_values
import csv

postgres_host = os.environ.get("VACHAN_POSTGRES_HOST", "localhost")
postgres_user = os.environ.get("VACHAN_POSTGRES_USER", "postgres")
postgres_database = os.environ.get("VACHAN_POSTGRES_DATABASE", "vachan")
postgres_password = os.environ.get("VACHAN_POSTGRES_PASSWORD", "secret")
postgres_port = os.environ.get("VACHAN_POSTGRES_PORT", "5432")
seed_db_file = "seed_DB.sql"

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
        * update data should containe 3 list with values csvColumnNum, Dict have that column name as key,
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
        header = next(csvreader)
        for table_row in csvreader:
            output_list.append(table_row)

try:
    command = """psql -U %s -p %s  --host %s --port %s %s < %s""" %\
        (postgres_user, postgres_password, postgres_host, postgres_port, postgres_database, seed_db_file)
    returnValue =  os.system(command)
    print("returnValue : ", returnValue)
    if returnValue == 0:
        # DB connection
        conn = psycopg2.connect(host=postgres_host, port=postgres_port,\
            dbname=postgres_database, user=postgres_user, password=postgres_password)
        cursor = conn.cursor()

        # get all permissions in db
        qry = "SELECT * FROM public.permissions ORDER BY permission_id ASC "
        cursor.execute(query=qry)
        permissison_data = cursor.fetchall()
        permission_heads = cursor.description
        PERMISSION_DICT= db_real_dict_cursor_to_dict_with_custom_key(permissison_data,\
            'permission_name', permission_heads)
        # get all resource types
        qry = "SELECT * FROM public.resource_types ORDER BY resource_type_id ASC "
        cursor.execute(query=qry)
        resource_type_data = cursor.fetchall()
        resource_type_heads = cursor.description
        RESOURCE_TYPE_DICT= db_real_dict_cursor_to_dict_with_custom_key(resource_type_data,\
            'resource_type_name', resource_type_heads)
        #get all apps
        qry = "SELECT * FROM public.apps ORDER BY app_id ASC "
        cursor.execute(query=qry)
        app_data = cursor.fetchall()
        app_heads = cursor.description
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
        insert_sql_access = "INSERT INTO public.access_rules (entitlement_id, tag_id, roles) VALUES %s"
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
        csv_table_modified_permission_map = update_csv_row_with_custom_fieldvalue_convert_to_tupple\
            (APIPERMISSIONTABLE, update_map)
        # insert converted tuple to DB
        insert_sql_map = "INSERT INTO public.api_permissions_map\
            (api_endpoint,method,request_app_id,filter_results,resource_type_id,permission_id) VALUES %s"
        execute_values(cursor, insert_sql_map, csv_table_modified_permission_map)
        conn.commit()
        print("Uploaded Api Permission Map CSV to DB ====>")
    else:
        raise("seed db have error running")

except Exception as err:
    print('error : ', err)

finally:
    if(conn):
        cursor.close()
        conn.close()