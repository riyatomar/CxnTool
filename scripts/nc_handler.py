
from scripts.file_utils import update_cnx_value

def handle_mod_and_head(parser_output, new_entries, nc_count, ne_count):
    def is_wx_word_present(word, entries_set):
        """Check if a wx_word is already present in new_entries."""
        return word in entries_set

    # Cache existing words for fast lookup
    existing_words = {entry['original_word'] for entry in new_entries} | {entry['original_word'] for entry in parser_output if entry.get('original_word', '').startswith("[ne_")}

    # Find the highest used 'ne_*' index in existing words
    existing_ne_counts = [
        int(word[4:-1]) for word in existing_words
        if word.startswith("[ne_") and word[4:-1].isdigit()
    ]
    ne_count = max(existing_ne_counts, default=ne_count) + 1  # Update ne_count dynamically

    for i, item in enumerate(parser_output):
        if (
            item.get('dependency_relation') == 'pof__cn'
            and item.get('pos_tag') in ['NNC', 'NNPC']
            and not item.get('cnx_index')
        ):
            # Generate a unique index for the new entry
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

            # Update the item's CNX values
            update_cnx_value(item, nc_index, 'mod' if prefix == 'nc' else 'begin')

            # Create a new entry for this item
            new_nc_entry = {
                'index': nc_index,
                'original_word': f'[{prefix}_{current_count}]',
                'wx_word': f'[{prefix}_{current_count}]',
                'dependency_relation': item.get("dependency_relation"),
                'head_index': item.get('head_index'),  # Use the item's 'head_index' directly
            }
            new_entries.append(new_nc_entry)
            existing_words.add(new_nc_entry['original_word'])

            # Update relationships for this item
            head_index = int(item.get('head_index', -1))  # Assign head_index explicitly
            for target_item in parser_output:
                if int(target_item.get('index', -1)) == head_index:
                    target_item['cnx_index'] = nc_index
                    target_item['cnx_component'] = 'head' if prefix == 'nc' else 'inside'

                    # Update dependency relation and head index for the new entry
                    new_nc_entry['dependency_relation'] = target_item.get("dependency_relation")
                    new_nc_entry['head_index'] = target_item.get('head_index')

    return nc_count, ne_count
