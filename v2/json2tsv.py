import json

def convert_to_tsv(data):
    headers = ['index', 'wx_word', 'original_word', 'pos_tag', 'head_index', 'dependency_relation', 'cnx_index', 'cnx_component']
    tsv_data = []
    
    # Loop through each sentence in the response
    for response in data['response']:
        sentence_id = response['sentence_id']
        parser_output = response['parser_output']
        
        # Add the sentence ID as a section header
        tsv_data.append(f"<sentence_id={sentence_id}>")
        
        # Process the words in the parser output
        for word_data in parser_output:
            row = []
            for header in headers:
                row.append(str(word_data.get(header, '-')))
            tsv_data.append("\t".join(row))
        
        # Close the sentence section
        tsv_data.append(f"</sentence_id>\n\n")
    
    return "\n".join(tsv_data)

input_file = 'IO/cxn_json_out.txt'  
output_file = 'IO/cxn_tsv_out.tsv' 

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

tsv_output = convert_to_tsv(data)

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(tsv_output)
