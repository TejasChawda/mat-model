import json


def clear_json(json_file):
    with open(json_file, 'w') as json_file:
        json_file.write('[]')


def get_scales_from_json(json_file):
    scales = set()

    with open(json_file, 'r') as file:
        json_data = json.load(file)

        for data in json_data:
            scales.add(data["Scale"])

    return scales
