import json, re
from wxconv import WXC
from constant.cc import *
from constant.units import *

# Utility Functions
def read_json_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def devanagari_to_wx(word):
    wxc = WXC()
    wx_text = wxc.convert(word)
    return wx_text

def update_cnx_value(item, new_value):
    """Update the cnx_value field, converting it to a list if necessary."""
    if 'cnx_value' in item:
        if isinstance(item['cnx_value'], str):
            item['cnx_value'] = [item['cnx_value'], new_value]
        elif isinstance(item['cnx_value'], list):
            item['cnx_value'].append(new_value)
    else:
        item['cnx_value'] = new_value

def integrate_ner_annotations(ner_output, parser_output, ne_count, new_entries):
    """Integrate NER annotations into the parser output with grouping for B- and I- annotations, adding ne_index to cnx_value."""
    ner_annotations = {ann["word"]: ann["annotation"] for ann in ner_output["data"][0]["annotation"]}
    in_ne_sequence = False  # Tracks if we're in a consecutive B-I sequence

    for item in parser_output:
        original_word = item.get("original_word", "")
        annotation = ner_annotations.get(original_word, "O")
        ner_value = annotation.split('-')[0]
        if annotation.startswith("B-"):
            # Start a new NER entity if a new B- tag appears
            if in_ne_sequence:
                # If already in a sequence, increment ne_count for a new entity
                ne_count += 1
            in_ne_sequence = True  # Mark that we're in an NE sequence

            # Set ne_index for the current entity and update cnx_value with ne_count and ne_index
            ne_index = len(parser_output) + len(new_entries) + 1
            update_cnx_value(item, f'{ne_index}:{ner_value}')
            
            # Create a new entry in new_entries
            new_ne_entry = {
                'index': ne_index,
                'original_word': f'[ne_{ne_count}]',
                'wx_word': f'[ne_{ne_count}]',
            }
            new_entries.append(new_ne_entry)

        elif annotation.startswith("I-") and in_ne_sequence:
            # Continue the same NE sequence without incrementing ne_count, using the current annotation value
            update_cnx_value(item, f'{ne_index}:{ner_value}')

        else:
            # Reset the sequence if annotation is "O" or a different structure
            in_ne_sequence = False

    return parser_output, ne_count, new_entries


def handle_mod_and_head(parser_output, new_entries, nc_count):
    for i, item in enumerate(parser_output):
        if item.get('dependency_relation') == 'pof__cn' and item.get('pos_tag') in ['NNC', 'NNPC']:
            nc_index = len(parser_output) + len(new_entries) + 1
            update_cnx_value(item, f'{nc_index}:mod')
            
            if isinstance(item['cnx_value'], list):
                item['cnx_value'] = item['cnx_value'][0]

            new_nc_entry = {
                'index': nc_index,
                'original_word': f'[nc_{nc_count}]',
                'wx_word': f'[nc_{nc_count}]',
            }
            new_entries.append(new_nc_entry)
            nc_count += 1

            if i + 1 < len(parser_output):
                next_item = parser_output[i + 1]
                if next_item.get('dependency_relation') == 'pof__cn':
                    next_item['cnx_value'] = f'{nc_index}:head'
                    first_cnx_value = next_item.get('cnx_value')
                    second_cnx_value = f'{nc_index + 1}:mod'
                    next_item['cnx_value'] = first_cnx_value
                    new_nc_entry['cnx_value'] = second_cnx_value

            head_index = int(item.get('head_index', -1))
            for target_item in parser_output:
                if int(target_item.get('index', -1)) == head_index:
                    target_item['cnx_value'] = f'{nc_index}:head'
    return nc_count

def handle_pof_rvks_rbk(parser_output, new_entries, cp_count):
    nc_cnx_index = None
    for item in parser_output:
        if item.get('dependency_relation') in ['pof', 'rvks', 'rbk']:
            cp_index = len(parser_output) + len(new_entries) + 1
            update_cnx_value(item, f'{cp_index}:kriyAmUla')

            if isinstance(item['cnx_value'], list):
                nc_cnx_index = item['cnx_value'][0].split(':')[0]
                item['cnx_value'] = item['cnx_value'][0]

            new_cp_entry = {
                'index': cp_index,
                'original_word': f'[cp_{cp_count}]',
                'wx_word': f'[cp_{cp_count}]',
            }
            new_entries.append(new_cp_entry)
            cp_count += 1

            if nc_cnx_index is not None:
                for entry in new_entries:
                    if int(entry.get('index', -1)) == int(nc_cnx_index):
                        update_cnx_value(entry, f'{cp_index}:kriyAmUla')

            head_index = int(item.get('head_index', -1))
            for target_item in parser_output:
                if int(target_item.get('index', -1)) == head_index:
                    update_cnx_value(target_item, f'{cp_index}:verbalizer_B')

                    for j in range(parser_output.index(target_item) + 1, len(parser_output)):
                        next_item = parser_output[j]
                        if next_item.get('pos_tag') == 'VAUX':
                            update_cnx_value(next_item, f'{cp_index}:verbalizer_I')
                        else:
                            break
    return cp_count

def handle_measurement_units(parser_output, new_entries, meas_count, MEAS_UNITS):
    for i, item in enumerate(parser_output):
        wx_word = item.get('wx_word', '').strip()
        if any(unit in wx_word for unit in MEAS_UNITS):
            if i > 0:
                prev_item = parser_output[i - 1]
                prev_word = prev_item.get('wx_word', '')

                if re.search(r'\d', prev_word):
                    meas_index = len(parser_output) + len(new_entries) + 1
                    update_cnx_value(item, f'{meas_index}:unit')
                    update_cnx_value(prev_item, f'{meas_index}:count')
                    
                    meas_entry = {
                        'index': meas_index,
                        'original_word': f'[meas_{meas_count}]',
                        'wx_word': f'[meas_{meas_count}]'
                    }
                    new_entries.append(meas_entry)
                    meas_count += 1
    return meas_count

def handle_calendaric_units(parser_output, new_entries, calendaric_count, calendaric_unit):
    for i, item in enumerate(parser_output):
        wx_word = item.get('wx_word', '').strip()

        if any(unit in wx_word for unit in calendaric_unit):
            if i > 0:
                prev_item = parser_output[i - 1]
                prev_word = prev_item.get('wx_word', '')
                next_item = parser_output[i + 1]
                next_word = next_item.get('wx_word', '')

                if re.search(r'\d', prev_word):
                    calendaric_index = len(parser_output) + len(new_entries) + 1
                    update_cnx_value(item, f'{calendaric_index}:component_of')
                    update_cnx_value(prev_item, f'{calendaric_index}:component_of')
                    
                    calendaric_entry = {
                        'index': calendaric_index,
                        'original_word': f'[calendar_{calendaric_count}]',
                        'wx_word': f'[calendar_{calendaric_count}]'
                    }
                    new_entries.append(calendaric_entry)
                    calendaric_count += 1

                    if re.search(r'\d', next_word):
                        update_cnx_value(next_item, f'{calendaric_index}:component_of')
    return calendaric_count

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
                    if int(target_item.get('index', -1)) == head_index and target_item.get('dependency_relation') in ['k7t', 'k7p']:
                        span_index = len(parser_output) + len(new_entries) + 1
                        
                        new_entry = {
                            'index': span_index,
                            'original_word': f'[span_{span_count}]',
                            'wx_word': f'[span_{span_count}]'
                        }
                        new_entries.append(new_entry)
                        span_indexes[f'[span_{span_count}]'] = span_index
                        update_cnx_value(target_item, f'{span_index}:end')

                        if 'cnx_value' in target_item and isinstance(target_item['cnx_value'], list):
                            cnx1_index = target_item['cnx_value'][0].split(':')[0]
                            while len(target_item['cnx_value']) > 1:
                                target_item['cnx_value'].pop()
                            target_item['cnx_value'] = target_item['cnx_value'][0]

                        for item_to_update in parser_output:
                            if int(item_to_update.get('index', -1)) == start_item['head_index']:
                                update_cnx_value(item_to_update, f'{span_index}:start')

                                if 'cnx_value' in item_to_update and isinstance(item_to_update['cnx_value'], list):
                                    cnx2_index = item_to_update['cnx_value'][0].split(':')[0]
                                    while len(item_to_update['cnx_value']) > 1:
                                        item_to_update['cnx_value'].pop()
                                    item_to_update['cnx_value'] = item_to_update['cnx_value'][0]

                        for entry in new_entries:
                                if cnx2_index is not None and int(entry.get('index', -1)) == int(cnx2_index):
                                    update_cnx_value(entry, f'{span_index}:start')
                                if cnx1_index is not None and int(entry.get('index', -1)) == int(cnx1_index):
                                    update_cnx_value(entry, f'{span_index}:end')


                        span_count += 1
                        break
    return span_count

def handle_spatial_relations(parser_output, new_entries, spatial_count):
    # Handling NN/NNP and k7p relation with 'main'
    for i in range(len(parser_output)):
        item = parser_output[i]

        # Check if the word has pos_tag as 'NN' or 'NNP' and relation as 'k7p'
        if item.get('pos_tag') in ['NN', 'NNP'] and item.get('dependency_relation') == 'k7p':
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
                                'wx_word': f'[spatial_{spatial_count}]'
                            }
                            new_entries.append(new_entry)

                            update_cnx_value(item, f'{spatial_index}:whole')
                            update_cnx_value(next_item, f'{spatial_index}:part')
                            spatial_count += 1
                            break
                    break

    # New Rule: Handling 'r6' relation with 'k7p' and 'main'
    for item in parser_output:
        if item.get('pos_tag') in ['NN', 'NNP'] and item.get('dependency_relation') == 'r6':
            head_index = int(item.get('head_index', -1))

            # Find the word with index equal to this head_index and 'k7p' relation
            for k7p_item in parser_output:
                if (
                    int(k7p_item.get('index', -1)) == head_index and
                    k7p_item.get('dependency_relation') == 'k7p'
                ):
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
                                'wx_word': f'[spatial_{spatial_count}]'
                            }
                            new_entries.append(new_entry)

                            update_cnx_value(item, f'{spatial_index}:whole')
                            update_cnx_value(k7p_item, f'{spatial_index}:part')
                            spatial_count += 1
                            break

    return spatial_count

def handle_conjunctions(parser_output, new_entries, conj_count, disjunct_count, CONJ_LIST, DISJUNCT_LIST):
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
                    update_cnx_value(target_item, f'{cnx_index}:op{op_count}')
                    matching_items.append(target_item)
                    op_count += 1

            if matching_items and original_word in CONJ_LIST:
                conj_entry = {
                    'index': cnx_index,
                    'original_word': f'[conj_{conj_count}]',
                    'wx_word': f'[conj_{conj_count}]'
                }
                new_entries.append(conj_entry)
                conj_count += 1

                for item in matching_items:
                    update_cnx_value(item, f'{cnx_index}:op')

            elif matching_items and original_word in DISJUNCT_LIST:
                disjunct_entry = {
                    'index': cnx_index,
                    'original_word': f'[disjunct_{disjunct_count}]',
                    'wx_word': f'[disjunct_{disjunct_count}]'
                }
                new_entries.append(disjunct_entry)
                disjunct_count += 1

                for item in matching_items:
                    update_cnx_value(item, f'{cnx_index}:op')

    return conj_count, disjunct_count

def modify_json_data(json_data):
    # Initial counts
    span_count = 1
    cp_count = 1
    meas_count = 1
    calendaric_count = 1
    nc_count = 1
    disjunct_count = 1
    conj_count = 1
    spatial_count = 1
    ne_count = 1
    new_entries = []


    for response in json_data.get('response', []):
        parser_output = response.get('parser_output', [])

        # Step 1: Convert original words to WX format
        for item in parser_output:
            original_word = item.get('original_word', '')
            item['wx_word'] = devanagari_to_wx(original_word)
            # print(parser_output)
        # Step 2: Process each part of the parser_output
        parser_output, ne_count, new_entries = integrate_ner_annotations(ner_data, parser_output, ne_count, new_entries)
        nc_count = handle_mod_and_head(parser_output, new_entries, nc_count)
        cp_count = handle_pof_rvks_rbk(parser_output, new_entries, cp_count)
        meas_count = handle_measurement_units(parser_output, new_entries, meas_count, MEAS_UNITS)
        calendaric_count = handle_calendaric_units(parser_output, new_entries, calendaric_count, CALENDARIC_UNITS)
        span_count = handle_spans(parser_output, new_entries, span_count)
        spatial_count = handle_spatial_relations(parser_output, new_entries, spatial_count) 
        conj_count, disjunct_count = handle_conjunctions(parser_output, new_entries, conj_count, disjunct_count, CONJ_LIST, DISJUNCT_LIST)

        parser_output.extend(new_entries)

    return json_data  

# Example usage
file_path = 'IO/parser_input.txt'
ner_file_path = 'IO/ner_output.txt'
ner_data = read_json_from_file(ner_file_path)
json_data = read_json_from_file(file_path)
modified_data = modify_json_data(json_data)
# print(modified_data)
with open('IO/cxn_json_out.txt', 'w', encoding='utf-8') as file:
    json.dump(json_data, file, ensure_ascii=False, indent=4)

