from scripts.file_utils import update_cnx_value

def handle_conj_disjunct(parser_output, new_entries, conj_count, disjunct_count, conj_LIST, disjunct_LIST):
    for cc_item in parser_output:
        if cc_item.get('pos_tag') == 'CC':
            head_index = int(cc_item.get('head_index', -1))
            dep_rel = cc_item.get('dependency_relation', '')
            original_word = cc_item.get('original_word', '')
            op_count = 1
            matching_items = []

            for target_item in parser_output:
                if int(target_item.get('head_index', -1)) == head_index and target_item.get('dependency_relation', '') == dep_rel and target_item.get('pos_tag') != 'CC':
                    cnx_index = len(parser_output) + len(new_entries) + 1
                    updated = False  # Track whether `op_count` should be incremented
                    
                    if target_item.get('cnx_component') is not None:
                        already_index = target_item.get('cnx_index')
                        for entry in new_entries:
                            if int(entry.get('index', -1)) == int(already_index) and entry.get('cnx_component') is None:
                                update_cnx_value(entry, cnx_index, f'op{op_count}')
                                updated = True  # Mark this as a valid update
                                break  # Stop checking other entries once updated
                    else:
                        update_cnx_value(target_item, cnx_index, f'op{op_count}')
                        updated = True  # Mark this as a valid update

                    if updated:  # Increment `op_count` only if an update occurred
                        op_count += 1

                    matching_items.append(target_item)

            if matching_items and original_word in conj_LIST:
                conj_entry = {
                    'index': cnx_index,
                    'original_word': f'[conj_{conj_count}]',
                    'wx_word': f'[conj_{conj_count}]',
                    'dependency_relation': dep_rel,
                }
                new_entries.append(conj_entry)
                conj_count += 1

            elif matching_items and original_word in disjunct_LIST:
                disjunct_entry = {
                    'index': cnx_index,
                    'original_word': f'[disjunct_{disjunct_count}]',
                    'wx_word': f'[disjunct_{disjunct_count}]',
                    'dependency_relation': dep_rel,
                }
                new_entries.append(disjunct_entry)
                disjunct_count += 1

    return conj_count, disjunct_count

