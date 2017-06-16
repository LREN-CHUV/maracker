import json
from jsonschema import validate

files_to_test = ["simple-cmd-app.json", "simple-container-app.json"]

if __name__ == "__main__":
    with open('boutiques.0.4.schema.json', 'r') as f:
        boutiques_schema = json.loads(f.read())
        for app_file in files_to_test:
            with open(app_file, 'r') as descr_file:
                app_descr = json.loads(descr_file.read())
                validate(app_descr, boutiques_schema)
                print("%s file passed the test" % app_file)
