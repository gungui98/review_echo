# def clip_long_text(data_dict):
#     new_data_dict = data_dict.copy()
#     for k in data_dict.keys():
#         if isinstance(data_dict[k], str):
#             new_data_dict[k] = data_dict[k][:20] + '...'
#     return new_data_dict

MAX_STRING_LENGTH = 20


def clip_long_text(string):
    if isinstance(string, str):
        string = str(string)
    if len(string) > MAX_STRING_LENGTH:
        string = string[:MAX_STRING_LENGTH] + '...'
    return string