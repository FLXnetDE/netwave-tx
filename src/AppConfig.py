import yaml

class AppConfig:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data = self._load_yaml()

    def _load_yaml(self) -> dict:
        try:
            with open(self.filepath, 'r') as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            print(f"Config file not found: {self.filepath}")
            return {}
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            return {}

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def all(self) -> dict:
        return self.data
