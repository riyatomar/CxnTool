from constant.cc import CONJ_LIST, DISJUNCT_LIST
from constant.units import MEAS_UNITS, CALENDARIC_UNITS
from scripts.file_utils import read_json_from_file, write_json_to_file
from scripts.text_utils import devanagari_to_wx
from scripts.ner_handler import handle_ner_annotations
from scripts.nc_handler import handle_mod_and_head
from scripts.cp_handler import handle_pof_rvks_rbk
from scripts.meas_handler import handle_measurement_units
from scripts.calendar_handler import handle_calendaric_units
from scripts.spatial_handler import handle_spatial_relations
from scripts.span_handler import handle_spans
from scripts.conj_disjunct_handler import handle_conj_disjunct


def modify_json_data(json_data, ner_data):
    span_count = nc_count = cp_count = disjunct_count = conj_count = spatial_count = meas_count = calendaric_count = 1
    ne_count = 0
    new_entries = []

    for response in json_data.get('response', []):
        parser_output = response.get('parser_output', [])

        for item in parser_output:
            original_word = item.get('original_word', '')
            item['wx_word'] = devanagari_to_wx(original_word)

        parser_output, ne_count, new_entries = handle_ner_annotations(ner_data, parser_output, ne_count, new_entries)
        nc_count, ne_count = handle_mod_and_head(parser_output, new_entries, nc_count, ne_count)
        cp_count = handle_pof_rvks_rbk(parser_output, new_entries, cp_count)
        meas_count = handle_measurement_units(parser_output, new_entries, meas_count, MEAS_UNITS)
        calendaric_count = handle_calendaric_units(parser_output, new_entries, calendaric_count, CALENDARIC_UNITS)
        spatial_count = handle_spatial_relations(parser_output, new_entries, spatial_count)
        span_count = handle_spans(parser_output, new_entries, span_count)
        conj_count, disjunct_count = handle_conj_disjunct(parser_output, new_entries, conj_count, disjunct_count, CONJ_LIST, DISJUNCT_LIST)

        parser_output.extend(new_entries)

    return json_data

if __name__ == "__main__":
    ner_file_path = 'IO/ner_output.txt'
    parser_file_path = 'IO/parser_input.txt'
    output_file_path = 'IO/cxn_json_out.txt'

    ner_data = read_json_from_file(ner_file_path)
    parser_data = read_json_from_file(parser_file_path)

    modified_data = modify_json_data(parser_data, ner_data)
    write_json_to_file(modified_data, output_file_path)

