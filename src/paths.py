config_data = {}


def read_paths(all_file_path):
    with open(all_file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            config_data[key.strip()] = value.strip()

    return config_data
