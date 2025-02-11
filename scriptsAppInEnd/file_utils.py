import json

def read_json_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_json_to_file(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# def update_cnx_value(item, new_value):
#     """Update the cnx_value field, converting it to a list if necessary."""
#     if 'cnx_value' in item:
#         if isinstance(item['cnx_value'], str):
#             item['cnx_value'] = [item['cnx_value'], new_value]
#         elif isinstance(item['cnx_value'], list):
#             item['cnx_value'].append(new_value)
#     else:
#         item['cnx_value'] = new_value

def update_cnx_value(item, index, component):
    """
    Update the item with top-level cnx_index and cnx_component fields.
    Silently skips errors.
    """
    try:
        item["cnx_index"] = index
        item["cnx_component"] = component
    except (TypeError, KeyError):
        pass  # Silently ignore errors