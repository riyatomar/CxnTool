from scripts.file_utils import update_cnx_value
import re 

def handle_measurement_units(parser_output, new_entries, meas_count, meas_UNITS):
    for i, item in enumerate(parser_output):
        wx_word = item.get('wx_word', '').strip()
        if any(unit in wx_word for unit in meas_UNITS):
            if i > 0:
                prev_item = parser_output[i - 1]
                prev_word = prev_item.get('wx_word', '')

                if re.search(r'\d', prev_word):
                    meas_index = len(parser_output) + len(new_entries) + 1
                    update_cnx_value(item, meas_index, f'unit')
                    update_cnx_value(prev_item, meas_index, f'count')
                    
                    meas_entry = {
                        'index': meas_index,
                        'original_word': f'[meas_{meas_count}]',
                        'wx_word': f'[meas_{meas_count}]'
                    }
                    new_entries.append(meas_entry)
                    meas_count += 1
    return meas_count