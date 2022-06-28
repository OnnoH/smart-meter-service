import yaml


class Config:
    def __init__(self, configuration_file):
        self.config = None
        with open(configuration_file, "r") as file:
            try:
                self.config = yaml.safe_load(file)
            except yaml.YAMLError as exception:
                print(exception)
