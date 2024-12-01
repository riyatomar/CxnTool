from scripts.file_utils import update_cnx_value

def handle_spans(parser_output, new_entries, span_count):
    start_stack = []
    span_indexes = {}
    # Initialize cnx1_index and cnx2_index to ensure they have a default value
    cnx1_index = None
    cnx2_index = None

    for i, item in enumerate(parser_output):
        if item.get('original_word') == 'से':
            head_index = int(item.get('head_index', -1))
            start_stack.append({
                'index': int(item.get('index', -1)),
                'head_index': head_index
            })

        elif item.get('original_word') == 'तक':
            head_index = int(item.get('head_index', -1))
            if start_stack:
                start_item = start_stack.pop()

                for target_item in parser_output:
                    if int(target_item.get('index', -1)) == head_index and target_item.get('dependency_relation') in ['k7t', 'k7p', 'rsp']:
                        span_index = len(parser_output) + len(new_entries) + 1
                        
                        new_entry = {
                            'index': span_index,
                            'original_word': f'[SPAN_{span_count}]',
                            'wx_word': f'[SPAN_{span_count}]'
                        }
                        new_entries.append(new_entry)
                        span_indexes[f'[SPAN_{span_count}]'] = span_index
                        update_cnx_value(target_item, span_index, f'end')

                        if 'cnx_value' in target_item and isinstance(target_item['cnx_value'], list):
                            cnx1_index = target_item['cnx_value'][0].split(':')[0]
                            while len(target_item['cnx_value']) > 1:
                                target_item['cnx_value'].pop()
                            target_item['cnx_value'] = target_item['cnx_value'][0]

                        for item_to_update in parser_output:
                            if int(item_to_update.get('index', -1)) == start_item['head_index']:
                                update_cnx_value(item_to_update, span_index, f'start')

                                if 'cnx_value' in item_to_update and isinstance(item_to_update['cnx_value'], list):
                                    cnx2_index = item_to_update['cnx_value'][0].split(':')[0]
                                    while len(item_to_update['cnx_value']) > 1:
                                        item_to_update['cnx_value'].pop()
                                    item_to_update['cnx_value'] = item_to_update['cnx_value'][0]

                        for entry in new_entries:
                                if cnx2_index is not None and int(entry.get('index', -1)) == int(cnx2_index):
                                    update_cnx_value(entry, span_index, f'start')
                                if cnx1_index is not None and int(entry.get('index', -1)) == int(cnx1_index):
                                    update_cnx_value(entry, span_index, f'end')


                        span_count += 1
                        break
    return span_count
