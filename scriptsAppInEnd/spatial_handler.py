from scripts.file_utils import update_cnx_value

def handle_spatial_relations(parser_output, new_entries, spatial_count):
    # Handling NN/NNP and k7p relation with 'main'
    for i in range(len(parser_output)):
        item = parser_output[i]

        if i + 1 < len(parser_output):
            next_item = parser_output[i + 1]

        # Check if the word has pos_tag as 'NN' or 'NNP' and relation as 'k7p'
        if item.get('pos_tag') in ['NN', 'NNP'] and item.get('dependency_relation') == 'k7p' and next_item.get('pos_tag') == 'PSP':
            head_index = int(item.get('head_index', -1))
      
            # Search for the next word that matches the conditions
            for j in range(i + 1, len(parser_output)):
                next_item = parser_output[j]

                if (
                    next_item.get('pos_tag') in ['NN', 'NNP'] and
                    next_item.get('dependency_relation') == 'k7p' and
                    int(next_item.get('head_index', -1)) == head_index
                ):
                    # Check if the head_index points to a 'main' dependency
                    for head_item in parser_output:
                        if int(head_item.get('index', -1)) == head_index and head_item.get('dependency_relation') == 'main':
                            spatial_index = len(parser_output) + len(new_entries) + 1
                            new_entry = {
                                'index': spatial_index,
                                'original_word': f'[spatial_{spatial_count}]',
                                'wx_word': f'[spatial_{spatial_count}]',
                                'dependency_relation': item.get("dependency_relation"),
                                'head_index': item.get('head_index'),
                            }
                            new_entries.append(new_entry)

                            if item.get('cnx_component') is not None:
                                already_index = item.get('cnx_index')
                                for entry in new_entries:
                                    if int(entry.get('index', -1)) == int(already_index):
                                        update_cnx_value(entry, spatial_index, f'whole')
                            else:
                                update_cnx_value(item, spatial_index, f'whole')
                               

                            if next_item.get('cnx_component') is not None:
                                already_index = next_item.get('cnx_index')
                                for entry in new_entries:
                                    if int(entry.get('index', -1)) == int(already_index):
                                        update_cnx_value(entry, spatial_index, f'part')
                            else:
                                update_cnx_value(next_item, spatial_index, f'part')

                            spatial_count += 1
                            break
                    break

    # New Rule: Handling 'r6' relation with 'k7p' and 'main'
    for i, item in enumerate(parser_output):
        if item.get('pos_tag') in ['NN', 'NNP'] and item.get('dependency_relation') == 'r6':
            head_index = int(item.get('head_index', -1))

            # Ensure the next item is PSP and correctly related
            if i + 1 < len(parser_output):
                next_item = parser_output[i + 1]
                if next_item.get('pos_tag') == 'PSP':
                    # Find the word with index equal to this head_index and 'k7p' relation
                    for k7p_item in parser_output:
                        if (
                            int(k7p_item.get('index', -1)) == head_index and
                            k7p_item.get('dependency_relation') == 'k7p'
                        ):
                            # print('true')
                            # Check if the 'k7p' head_index points to 'main'
                            main_head_index = int(k7p_item.get('head_index', -1))
                            for main_item in parser_output:
                                if (
                                    int(main_item.get('index', -1)) == main_head_index and
                                    main_item.get('dependency_relation') == 'main'
                                ):
                                    spatial_index = len(parser_output) + len(new_entries) + 1
                                    new_entry = {
                                        'index': spatial_index,
                                        'original_word': f'[spatial_{spatial_count}]',
                                        'wx_word': f'[spatial_{spatial_count}]',
                                        'dependency_relation': 'k7p',
                                        'head_index': k7p_item.get('head_index'),
                                    }
                                    new_entries.append(new_entry)

                                    # Update 'whole' or 'part' connections
                                    if item.get('cnx_component') is not None:
                                        already_index = item.get('cnx_index')
                                        for entry in new_entries:
                                            if int(entry.get('index', -1)) == int(already_index):
                                                update_cnx_value(entry, spatial_index, f'whole')
                                    else:
                                        update_cnx_value(item, spatial_index, f'whole')

                                    if k7p_item.get('cnx_component') is not None:
                                        already_index = k7p_item.get('cnx_index')
                                        for entry in new_entries:
                                            if int(entry.get('index', -1)) == int(already_index):
                                                update_cnx_value(entry, spatial_index, f'part')
                                    else:
                                        update_cnx_value(k7p_item, spatial_index, f'part')

                                    spatial_count += 1
                                    break

    return spatial_count