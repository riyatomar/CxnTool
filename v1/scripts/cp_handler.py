from scripts.file_utils import update_cnx_value

def handle_pof_rvks_rbk(parser_output, new_entries, cp_count):
    nc_cnx_index = None
    for item in parser_output:
        if item.get('dependency_relation') in ['pof']: #, 'rvks', 'rbk', 'rsk']:
            cp_index = len(parser_output) + len(new_entries) + 1

            if item.get('cnx_component') is not None:
                already_index = item.get('cnx_index')
                for entry in new_entries:
                    if int(entry.get('index', -1)) == int(already_index):
                        update_cnx_value(entry, cp_index, f'kriyAmUla')
            else:
                update_cnx_value(item, cp_index, f'kriyAmUla')
          
            new_cp_entry = {
                'index': cp_index,
                'original_word': f'[cp_{cp_count}]',
                'wx_word': f'[cp_{cp_count}]',
            }
            new_entries.append(new_cp_entry)
            cp_count += 1

            head_index = int(item.get('head_index', -1))
            for target_item in parser_output:
                if int(target_item.get('index', -1)) == int(head_index):
                    update_cnx_value(target_item, cp_index, f'verbalizer_B')

                    for j in range(parser_output.index(target_item) + 1, len(parser_output)):
                        next_item = parser_output[j]
                        if next_item.get('pos_tag') == 'VAUX':
                            update_cnx_value(next_item, cp_index, f'verbalizer_I')
                        else:
                            break
    return cp_count
    