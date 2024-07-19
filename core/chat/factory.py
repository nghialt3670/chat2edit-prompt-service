from typing import Any, Iterable

from chat2edit.utils.file import read_yamls


class Factory:
    def __init__(self, yaml_config_files: Iterable[str]) -> None:
        self.config = read_yamls(yaml_config_files)
        self.context = {}

    def __call__(self, class_name: str, **kwargs) -> Any:
        if class_name in self.context:
            return self.context[class_name]

        class_path = self.config[class_name]["class_path"]
        module_path, _ = class_path.rsplit(".", 1)
        module = __import__(module_path, fromlist=[class_name])
        obj_class = getattr(module, class_name)
        obj_params = {}
        params_config = self.config[class_name]["params"]
        for key, value in params_config.items():
            obj_params[key] = (
                self(value["reference"])
                if isinstance(value, dict) and "reference" in value
                else value
            )
        obj_params.update(kwargs)
        obj = obj_class(**obj_params)
        self.context[class_name] = obj
        return obj
