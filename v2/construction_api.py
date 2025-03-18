from flask import Flask, request, jsonify
import requests
from constant.cc import CONJ_LIST, DISJUNCT_LIST
from constant.units import MEAS_UNITS, CALENDARIC_UNITS
from scripts.text_utils import devanagari_to_wx
from scripts.ner_handler import handle_ner_annotations
from scripts.nc_handler import handle_mod_and_head
from scripts.cp_handler import handle_pof_rvks_rbk
from scripts.meas_handler import handle_measurement_units
from scripts.calendar_handler import handle_calendaric_units
from scripts.spatial_handler import handle_spatial_relations
from scripts.span_handler import handle_spans
from scripts.conj_disjunct_handler import handle_conj_disjunct

app = Flask(__name__)

# API endpoints for external services
url1 = "http://10.2.8.12:8080/get_ner_entities"
url2 = "http://10.2.8.12:4000/parser/get_parser_output"

# Function to fetch entities from API
def get_entities(api_url, payload):
    try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 200:
            return response.json()  # Parse JSON response
        else:
            return {"error": f"Request failed with status code {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# Function to modify JSON data
def modify_json_data(json_data, ner_data):
    for response in json_data.get('response', []):
        parser_output = response.get('parser_output', [])

        # Reinitialize counters and temporary lists for each sentence
        span_count = nc_count = cp_count = disjunct_count = conj_count = spatial_count = meas_count = calendaric_count = 1
        ne_count = 0
        new_entries = []

        # Preprocess the parser_output
        for item in parser_output:
            original_word = item.get('original_word', '')
            item['wx_word'] = devanagari_to_wx(original_word)

        # Process annotations and relations
        parser_output, ne_count, new_entries = handle_ner_annotations(ner_data, parser_output, ne_count, new_entries)
        nc_count, ne_count = handle_mod_and_head(parser_output, new_entries, nc_count, ne_count)
        cp_count = handle_pof_rvks_rbk(parser_output, new_entries, cp_count)
        meas_count = handle_measurement_units(parser_output, new_entries, meas_count, MEAS_UNITS)
        calendaric_count = handle_calendaric_units(parser_output, new_entries, calendaric_count, CALENDARIC_UNITS)
        spatial_count = handle_spatial_relations(parser_output, new_entries, spatial_count)
        span_count = handle_spans(parser_output, new_entries, span_count)
        conj_count, disjunct_count = handle_conj_disjunct(parser_output, new_entries, conj_count, disjunct_count, CONJ_LIST, DISJUNCT_LIST)

        # Append the new entries to the parser output
        parser_output.extend(new_entries)

    return json_data


# API endpoint to process data
@app.route('/construction_tool', methods=['POST'])
def process_data():
    try:
        # Step 1: Read input JSON from request
        input_data = request.get_json()
        if not input_data:
            return jsonify({"error": "No input data provided"}), 400

        # Step 2: Fetch NER entities from the first API
        ner_data = get_entities(url1, input_data)
        if "error" in ner_data:
            return jsonify({"error": f"NER API Error: {ner_data['error']}"}), 500

        # Step 3: Fetch parser output from the second API
        parser_data = get_entities(url2, input_data)
        if "error" in parser_data:
            return jsonify({"error": f"Parser API Error: {parser_data['error']}"}), 500

        # Step 4: Modify the parser data with NER data
        modified_data = modify_json_data(parser_data, ner_data)

        # Step 5: Return the final modified JSON
        return jsonify(modified_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
