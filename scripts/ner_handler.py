from scripts.file_utils import update_cnx_value

def handle_ner_annotations(ner_output, parser_output, ne_count, new_entries):
    """Integrate NER annotations into the parser output."""
    if not isinstance(ner_output, dict) or "data" not in ner_output:
        raise ValueError("Invalid NER output format. Expected a dictionary with a 'data' key.")

    if not isinstance(ner_output["data"], list) or not ner_output["data"]:
        raise ValueError("Invalid NER data structure. 'data' should be a non-empty list.")

    sentence_annotations = ner_output["data"][0].get("annotation", [])
    if not isinstance(sentence_annotations, list):
        raise ValueError("Invalid 'annotation' structure in NER data. Expected a list.")

    ner_annotations = {ann["word"]: ann["annotation"] for ann in sentence_annotations}

    in_ne_sequence = False
    current_entity_type = None
    entity_count = {"PER": 0, "LOC": 0, "ORG": 0}
    last_dependency_relation = last_head_index = None
    ne_index = None  # Track the index of the current NE for updates

    for item in parser_output:
        original_word = item.get("original_word", "")
        annotation = ner_annotations.get(original_word, "O")
        ner_value = "begin" if annotation.startswith("B-") else "inside" if annotation.startswith("I-") else "O"

        if annotation.startswith("B-"):
            if in_ne_sequence:
                in_ne_sequence = False  # End the previous entity sequence

            in_ne_sequence = True
            current_entity_type = annotation.split('-')[1]
            entity_count[current_entity_type] += 1
            ne_index = len(parser_output) + len(new_entries) + 1
            ne_count += 1

            wx_word = f'{current_entity_type}_{entity_count[current_entity_type]}'
            last_dependency_relation = item.get("dependency_relation")  # Set relation for the start of the new entity
            last_head_index = item.get('head_index')
            update_cnx_value(item, ne_index, ner_value)

            new_entries.append({
                'index': ne_index,
                'original_word': wx_word.lower(),
                'wx_word': f'[ne_{ne_count}]',
                'dependency_relation': last_dependency_relation,
                'head_index': last_head_index,
            })

        elif annotation.startswith("I-"):
            entity_type = annotation.split('-')[1]
            if in_ne_sequence and entity_type == current_entity_type:
                last_dependency_relation = item.get("dependency_relation")  # Update to current token's relation
                last_head_index = item.get('head_index')
                update_cnx_value(item, ne_index, ner_value)
            elif in_ne_sequence and entity_type != current_entity_type:
                # Transition to a new entity type
                in_ne_sequence = True
                current_entity_type = entity_type
                entity_count[current_entity_type] += 1
                ne_index = len(parser_output) + len(new_entries) + 1
                ne_count += 1

                wx_word = f'{current_entity_type}_{entity_count[current_entity_type]}'
                last_dependency_relation = item.get("dependency_relation")
                last_head_index = item.get('head_index')

                new_entries.append({
                    'index': ne_index,
                    'original_word': wx_word.lower(),
                    'wx_word': f'[ne_{ne_count}]',
                    'dependency_relation': last_dependency_relation,
                    'head_index': last_head_index,
                })
            else:
                in_ne_sequence = False
                current_entity_type = None
        else:
            in_ne_sequence = False
            current_entity_type = None

    # Correct dependency relation for the last added NE entry
    if new_entries:
        new_entries[-1]['dependency_relation'] = last_dependency_relation
        new_entries[-1]['head_index'] = last_head_index

    return parser_output, ne_count, new_entries
