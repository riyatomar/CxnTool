from scripts.file_utils import update_cnx_value
from constant.cc import COMP_LIST

def handle_compound(parser_output, new_entries, compound_count):
    for i, item in enumerate(parser_output):        
        prev_item = parser_output[i - 1] if i > 0 else None 
        # if i < len(parser_output) - 1:
        #     next_item = parser_output[i + 1]

        if prev_item is not None and prev_item.get('pos_tag', '') in ['NN', 'NNP', 'NNPC'] and item.get('pos_tag', '') == 'JJ' and item.get('wx_word', '') in COMP_LIST:
            compound_index = len(parser_output) + len(new_entries) + 1
            update_cnx_value(item, compound_index, f'head')
            update_cnx_value(prev_item, compound_index, f'mod')
            
            compound_entry = {
                'index': compound_index,
                'original_word': f'[compound_{compound_count}]',
                'wx_word': f'[compound_{compound_count}]',
                'dependency_relation': item.get("dependency_relation"),
                'head_index': item.get('head_index'),
            }
            new_entries.append(compound_entry)
            compound_count += 1
    return compound_count
