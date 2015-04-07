import os
import yaml


LOCAL_STORAGE_PATH = ".mathquiz"


def get_local_storage_dir():
    home_path = os.getenv("HOME")
    return os.path.join(home_path, LOCAL_STORAGE_PATH)


def init_local_storage(user):
    local_storage_dir = get_local_storage_dir()

    if os.path.isdir(local_storage_dir):
        return

    os.mkdir(local_storage_dir)


def get_user_yaml_path(user):
    local_storage_dir = get_local_storage_dir()
    user_yaml = os.path.join(local_storage_dir, "%s.yaml" % user)
    return user_yaml


def get_default_user_data():
    return dict(results=[])


def get_current_user_data(user):
    user_yaml_path = get_user_yaml_path(user)
    if os.path.exists(user_yaml_path):
        contents = open(user_yaml_path, "r").read()
        return yaml.load(contents)
    return get_default_user_data()


def store_quiz_results_local(user, results):
    init_local_storage(user)
    user_yaml_path = get_user_yaml_path(user)
    current_user_data = get_current_user_data(user)
    current_user_data['results'].append(results)
    yaml_out = yaml.dump(current_user_data)

    with open(user_yaml_path, "w") as user_yaml_file:
        user_yaml_file.write(yaml_out)
