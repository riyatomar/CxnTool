from scripts.file_utils import update_cnx_value

def handle_conj_disjunct(parser_output, new_entries, conj_count, disjunct_count, CONJ_LIST, DISJUNCT_LIST):
    for cc_item in parser_output:
        if cc_item.get('pos_tag') == 'CC':
            head_index = int(cc_item.get('head_index', -1))
            dep_rel = cc_item.get('dependency_relation', '')
            original_word = cc_item.get('original_word', '')
            op_count = 1
            matching_items = []
            cxn_value1_index = None
            cxn_value2_index = None
            cxn_value1_component = None
            cxn_value2_component = None


            for target_item in parser_output:
                if int(target_item.get('head_index', -1)) == head_index and target_item.get('dependency_relation', '') == dep_rel and target_item.get('pos_tag') != 'CC':
                    cnx_index = len(parser_output) + len(new_entries) + 1
                    update_cnx_value(target_item, cnx_index, f'op{op_count}')
                    
                    if isinstance(target_item['cnx_index'], list) and len(target_item['cnx_index']) > 1:
                        cxn_value1_index = target_item['cnx_index'][0]
                        cxn_value1_component = target_item['cnx_component'][0]

                        cxn_value2_index = target_item['cnx_index'][1]
                        cxn_value2_component = target_item['cnx_component'][1]

                        target_item['cnx_index'] = target_item['cnx_index'][0]
                        target_item['cnx_component'] = target_item['cnx_component'][0]
                    else:
                        continue

                    for entry in new_entries:
                        if entry.get('index') == int(cxn_value1_index):
                            entry['cnx_index'] = cxn_value2_index
                            entry['cnx_component'] = cxn_value2_component

                    
                    matching_items.append(target_item)
                    op_count += 1

            if matching_items and original_word in CONJ_LIST:
                conj_entry = {
                    'index': cnx_index,
                    'original_word': f'[CONJ_{conj_count}]',
                    'wx_word': f'[CONJ_{conj_count}]'
                }
                new_entries.append(conj_entry)
                conj_count += 1

            elif matching_items and original_word in DISJUNCT_LIST:
                disjunct_entry = {
                    'index': cnx_index,
                    'original_word': f'[DISJUNCT_{disjunct_count}]',
                    'wx_word': f'[DISJUNCT_{disjunct_count}]'
                }
                new_entries.append(disjunct_entry)
                disjunct_count += 1

    return conj_count, disjunct_count

