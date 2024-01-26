#! /usr/bin/env python3

# TODO Decide if this is a valid approach
# import json

# from senzing import g2engine_with_info
# from senzing.g2exception import G2Exception

# ini_params_dict = {
#     "PIPELINE": {
#         "CONFIGPATH": "/etc/opt/senzing",
#         "RESOURCEPATH": "/opt/senzing/g2/resources",
#         "SUPPORTPATH": "/opt/senzing/data",
#     },
#     "SQL": {"CONNECTION": "sqlite3://na:na@/tmp/sqlite/G2C.db"},
# }
# module_name = "Example"

# data_source_code = "TEST"
# record_id_1 = "Example-1"
# record_id_2 = "Example-2"
# record = {
#     "RECORD_TYPE": "PERSON",
#     "PRIMARY_NAME_LAST": "Smith",
#     "PRIMARY_NAME_FIRST": "Robert",
#     "DATE_OF_BIRTH": "12/11/1978",
#     "ADDR_TYPE": "MAILING",
#     "ADDR_LINE1": "123 Main Street, Las Vegas NV 89132",
#     "PHONE_TYPE": "HOME",
#     "PHONE_NUMBER": "702-919-1300",
#     "EMAIL_ADDRESS": "bsmith@work.com",
#     "DATE": "1/2/18",
#     "STATUS": "Active",
#     "AMOUNT": "100",
# }

# iterations = 10

# add_with_info_responses = g2engine_with_info.WithInfoResponses()

# try:
#     g2_engine = g2engine_with_info.G2Engine(module_name, json.dumps(ini_params_dict))
#     for _ in range(iterations):
#         g2_engine.add_record(
#             data_source_code,
#             record_id_2,
#             json.dumps(record),
#             with_info_obj=add_with_info_responses,
#         )
# except G2Exception as err:
#     print(err)

# current_responses = add_with_info_responses.get_and_clear()
# while current_responses:
#     print(current_responses.pop())
