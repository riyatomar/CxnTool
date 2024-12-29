from scripts.file_utils import update_cnx_value
import re

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
                    update_cnx_value(item, calendaric_index, f'component_of')
                    update_cnx_value(prev_item, calendaric_index, f'component_of')
                    
                    calendaric_entry = {
                        'index': calendaric_index,
                        'original_word': f'[calendar_{calendaric_count}]',
                        'wx_word': f'[calendar_{calendaric_count}]'
                    }
                    new_entries.append(calendaric_entry)
                    calendaric_count += 1

                    if re.search(r'\d', next_word):
                        update_cnx_value(next_item, calendaric_index, f'component_of')
    return calendaric_count
