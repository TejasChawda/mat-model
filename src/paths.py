config_data = {}


def read_paths():
    config_file_path = '/Users/admin/Desktop/pythonStreamlitDemo/Files/Paths.txt'
    with open(config_file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            config_data[key.strip()] = value.strip()

    return config_data

