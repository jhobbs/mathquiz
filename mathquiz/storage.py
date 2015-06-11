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
    return dict(results=[], unanswered_questions=[])


def get_current_user_data(user):
    user_yaml_path = get_user_yaml_path(user)
    if os.path.exists(user_yaml_path):
        contents = open(user_yaml_path, "r").read()
        return yaml.load(contents)
    return get_default_user_data()


def add_to_local_storage_list(user, list_name, item):
    init_local_storage(user)
    user_yaml_path = get_user_yaml_path(user)
    current_user_data = get_current_user_data(user)
    current_user_data[list_name].append(item)
    yaml_out = yaml.dump(current_user_data)

    with open(user_yaml_path, "w") as user_yaml_file:
        user_yaml_file.write(yaml_out)


def store_quiz_results_local(user, results):
    add_to_local_storage_list(user, 'results', results)


def add_unanswered_question(user, question):
    add_to_local_storage_list(user, 'unanswered_questions', question)


def get_unanswered_question(user, question_uuid):
    user_data = get_current_user_data(user)
    for question in user_data['unanswered_questions']:
        if question.uuid == question_uuid:
            return question

    return None
