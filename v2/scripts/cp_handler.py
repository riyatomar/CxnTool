from scripts.file_utils import update_cnx_value

def handle_pof_rvks_rbk(parser_output, new_entries, cp_count):
    last_dependency_relation = None  # Initialize last_dependency_relation

    for item in parser_output:
        if item.get('dependency_relation') in ['pof']:  # Add other relations if needed: 'rvks', 'rbk', 'rsk'
            cp_index = len(parser_output) + len(new_entries) + 1

            # Update last_dependency_relation for the current item
            # last_dependency_relation = item.get('dependency_relation')

            if item.get('cnx_component') is not None:
                already_index = item.get('cnx_index')
                for entry in new_entries:
                    if int(entry.get('index', -1)) == int(already_index):
                        update_cnx_value(entry, cp_index, f'kriyAmUla')
            else:
                update_cnx_value(item, cp_index, f'kriyAmUla')

            head_index = int(item.get('head_index', -1))
            for target_item in parser_output:
                if int(target_item.get('index', -1)) == int(head_index):
                    # update_cnx_value(target_item, cp_index, f'verbalizer_B')
                    update_cnx_value(target_item, cp_index, f'verbalizer')

                    # Update last_dependency_relation with the dependency relation of target_item
                    last_dependency_relation = target_item.get('dependency_relation')
                    last_head_index = target_item.get('head_index')

                    for j in range(parser_output.index(target_item) + 1, len(parser_output)):
                        next_item = parser_output[j]
                        if next_item.get('pos_tag') == 'VAUX':
                            # update_cnx_value(next_item, cp_index, f'verbalizer_I')
                            update_cnx_value(next_item, cp_index, f'verbalizer')
                        else:
                            break

            # Create a new CP entry with the updated last_dependency_relation
            new_cp_entry = {
                'index': cp_index,
                'original_word': f'[cp_{cp_count}]',
                'wx_word': f'[cp_{cp_count}]',
                'dependency_relation': last_dependency_relation,  # Attach the last_dependency_relation here
                'head_index': last_head_index,
            }
            new_entries.append(new_cp_entry)
            cp_count += 1

    return cp_count
