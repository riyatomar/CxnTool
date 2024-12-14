from scripts.file_utils import update_cnx_value

def handle_spans(parser_output, new_entries, span_count):
    start_stack = []
    span_indexes = {}

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
                            'original_word': f'[span_{span_count}]',
                            'wx_word': f'[span_{span_count}]'
                        }
                        new_entries.append(new_entry)
                        span_indexes[f'[span_{span_count}]'] = span_index

                        if target_item.get('cnx_component') is not None:
                            already_index = target_item.get('cnx_index')
                            for entry in new_entries:
                                if int(entry.get('index', -1)) == int(already_index):
                                    update_cnx_value(entry, span_index, f'end')
                        else:
                            update_cnx_value(target_item, span_index, f'end')

                        for item_to_update in parser_output:
                            if int(item_to_update.get('index', -1)) == start_item['head_index']:
                                if item_to_update.get('cnx_component') is not None:
                                    already_index = item_to_update.get('cnx_index')
                                    for entry in new_entries:
                                        if int(entry.get('index', -1)) == int(already_index):
                                            update_cnx_value(entry, span_index, f'start')
                                else:
                                    update_cnx_value(item_to_update, span_index, f'start')
                                

                        span_count += 1
                        break
    return span_count
