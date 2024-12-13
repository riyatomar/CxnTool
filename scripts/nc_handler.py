from scripts.file_utils import update_cnx_value

def handle_mod_and_head(parser_output, new_entries, nc_count, ne_count):
    def is_wx_word_present(word, entries_set):
        """Check if a wx_word is already present in new_entries."""
        return word in entries_set

    # Cache existing words for fast lookup
    existing_words = {entry['original_word'] for entry in new_entries}

    for i, item in enumerate(parser_output):
        if item.get('dependency_relation') == 'pof__cn' and item.get('pos_tag') in ['NNC', 'NNPC']:
            # Skip if already has cnx_index
            if 'cnx_index' in item and item['cnx_index']:
                continue

            nc_index = len(parser_output) + len(new_entries) + 1
            prefix = 'nc' if item.get('pos_tag') == 'NNC' else 'ne'
            current_count = nc_count if prefix == 'nc' else ne_count

            # Ensure unique naming
            while is_wx_word_present(f'[{prefix}_{current_count}]', existing_words):
                current_count += 1

            # Increment counts for the next item
            if prefix == 'nc':
                nc_count = current_count + 1
            else:
                ne_count = current_count + 1

            update_cnx_value(item, nc_index, 'mod' if prefix == 'nc' else 'begin')

            # Add new entry for the current `pof__cn`
            new_nc_entry = {
                'index': nc_index,
                'original_word': f'[{prefix}_{current_count}]',
                'wx_word': f'[{prefix}_{current_count}]',
            }
            new_entries.append(new_nc_entry)
            existing_words.add(new_nc_entry['original_word'])

            # Update relationships for this item
            head_index = int(item.get('head_index', -1))
            # print(head_index)
            for target_item in parser_output:
                if int(target_item.get('index', -1)) == head_index:
                    print(target_item.get('cnx_index'), target_item.get('cnx_component'))
                    target_item['cnx_index'] = nc_index
                    target_item['cnx_component'] = 'head' if prefix == 'nc' else 'inside'

    return nc_count, ne_count


# add "(target_item.get('cnx_index'), target_item.get('cnx_component'))" in the cnx_index and cnx_component of previous new_nc_entry