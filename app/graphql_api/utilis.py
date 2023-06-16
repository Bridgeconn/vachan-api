# '''Utility functions to be used in graphql API implementations'''
# from schema import schemas_nlp
# def convert_graphene_obj_to_pydantic(input_obj, target_class):
#     '''convert a graphene input object into specified pydantic model'''
#     kwargs = {}
#     for key in input_obj:
#         kwargs[key] = input_obj[key]
#     new_obj = target_class(**kwargs)
#     return new_obj

# def swtype_converison(res):
#     '''find sw type from confidence value'''
#     if not 'stopwordType' in res.keys():
#         if 'confidence' in res.keys():
#             if res['confidence'] == 2:
#                 res['stopwordType'] = schemas_nlp.StopWordsType.SYSTEM.value
#             elif res['confidence'] == 1:
#                 res['stopwordType'] = schemas_nlp.StopWordsType.USER.value
#             else:
#                 res['stopwordType'] = schemas_nlp.StopWordsType.AUTO.value
#             if res['confidence'] in [1, 2]:
#                 res['confidence'] = None
#     return res