from scripts.file_utils import update_cnx_value

def handle_mod_and_head(parser_output, new_entries, nc_count, ne_count):
    def is_wx_word_present(word, entries_set):
        """Check if a wx_word is already present in new_entries."""
        return word in entries_set

    # Cache existing words for fast lookup
    existing_words = {entry['original_word'] for entry in new_entries}
    last_dependency_relation = None
    for i, item in enumerate(parser_output):
        if (
            item.get('dependency_relation') == 'pof__cn'
            and item.get('pos_tag') in ['NNC', 'NNPC']
            and not item.get('cnx_index')
        ):
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

            last_dependency_relation = item.get("dependency_relation")
            update_cnx_value(item, nc_index, 'mod' if prefix == 'nc' else 'begin')
            
            # Add new entry for the current `pof__cn`
            new_nc_entry = {
                'index': nc_index,
                'original_word': f'[{prefix}_{current_count}]',
                'wx_word': f'[{prefix}_{current_count}]',
                'dependency_relation': last_dependency_relation,
            }
            new_entries.append(new_nc_entry)
            existing_words.add(new_nc_entry['original_word'])

            # Update relationships for this item
            head_index = int(item.get('head_index', -1))
            for target_item in parser_output:
                if int(target_item.get('index', -1)) == head_index:
                    target_item['cnx_index'] = nc_index
                    target_item['cnx_component'] = 'head' if prefix == 'nc' else 'inside'
                    final_dep_rel = target_item.get("dependency_relation")
                    new_nc_entry['dependency_relation'] = final_dep_rel

    return nc_count, ne_count
