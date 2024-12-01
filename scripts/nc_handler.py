from scripts.file_utils import update_cnx_value

def handle_mod_and_head(parser_output, new_entries, nc_count, ne_count):
    def is_wx_word_present(word, entries):
        """Check if a wx_word is already present in new_entries."""
        return any(entry.get('original_word') == word for entry in entries)

    for i, item in enumerate(parser_output):
        if item.get('dependency_relation') == 'pof__cn' and item.get('pos_tag') in ['NNC', 'NNPC']:
            if 'cnx_index' in item and item['cnx_index']:
                continue
             
            nc_index = len(parser_output) + len(new_entries) + 1

            # Determine the prefix, counter, and cnx_value structure based on the pos_tag
            if item.get('pos_tag') == 'NNC':
                prefix = 'NC'
                current_count = nc_count
                while is_wx_word_present(f'[{prefix}_{current_count}]', new_entries):
                    current_count += 1  # Ensure uniqueness
                nc_count = current_count + 1
                update_cnx_value(item, nc_index, f'mod')
            elif item.get('pos_tag') == 'NNPC':
                prefix = 'NE'
                current_count = ne_count
                while is_wx_word_present(f'[{prefix}_{current_count}]', new_entries):
                    current_count += 1  # Ensure uniqueness
                ne_count = current_count + 1
                update_cnx_value(item, nc_index, f'begin')

            if isinstance(item['cnx_index'], list):
                item['cnx_index'] = item['cnx_index'][0]
                item['cnx_component'] = item['cnx_component'][0]

            # Create a new entry with appropriate `wx_word`
            new_nc_entry = {
                'index': nc_index,
                'original_word': f'[{prefix}_{current_count}]',
                'wx_word': f'[{prefix}_{current_count}]',
            }
            new_entries.append(new_nc_entry)

            # Adjust `cnx_value` for the next item in sequence if it matches criteria
            if i + 1 < len(parser_output):
                next_item = parser_output[i + 1]
                if next_item.get('dependency_relation') == 'pof__cn':
                    if item.get('pos_tag') == 'NNC':
                        next_item['cnx_index'] = nc_index
                        next_item['cnx_component'] = 'head'
                    elif item.get('pos_tag') == 'NNPC':
                        next_item['cnx_index'] = nc_index
                        next_item['cnx_component'] = 'inside'

                    # first_cnx_value = next_item.get('cnx_value')
                    first_cnx_index = next_item.get('cnx_index')
                    first_cnx_component = next_item.get('cnx_component')

                    # second_cnx_value = f'{nc_index + 1}:mod' if item.get('pos_tag') == 'NNC' else f'{nc_index + 1}:B'
                    second_cnx_index = f'{nc_index + 1}' if item.get('pos_tag') == 'NNC' else f'{nc_index + 1}'
                    second_cnx_component = 'mod' if item.get('pos_tag') == 'NNC' else 'begin'

                    next_item['cnx_index'] = first_cnx_index
                    next_item['cnx_component'] = first_cnx_component
                    new_nc_entry['cnx_index'] = second_cnx_index
                    new_nc_entry['cnx_component'] = second_cnx_component

            # Update the `cnx_value` of the target item's head if applicable
            head_index = int(item.get('head_index', -1))
            for target_item in parser_output:
                if int(target_item.get('index', -1)) == head_index:
                    if item.get('pos_tag') == 'NNC':
                        target_item['cnx_index'] = nc_index
                        target_item['cnx_component'] = 'head'
                    elif item.get('pos_tag') == 'NNPC':
                        target_item['cnx_index'] = nc_index
                        target_item['cnx_component'] = 'inside'

    return nc_count, ne_count
