import re
import json


class DataModelBase:
    def serialize_to_json(self):
        snake_case_dict = self.__dict__
        camel_case_dict = dict()
        for key, value in snake_case_dict.items():
            if isinstance(value, DataModelBase):
                camel_case_dict[DataModelBase.snake_case_to_camel_case(key)] = value.serialize_to_json()
            elif isinstance(value, list):
                if len(value) > 0:
                    if isinstance(value[0], DataModelBase):
                        camel_case_dict[DataModelBase.snake_case_to_camel_case(key)] = [
                            v.serialize_to_json() for v in value
                        ]
            elif value is not None:
                camel_case_dict[DataModelBase.snake_case_to_camel_case(key)] = value
        return camel_case_dict

    @staticmethod
    def snake_case_to_camel_case(snake_case):
        components = snake_case.split('_')
        camel_case = components[0] + ''.join(x.title() for x in components[1:])
        return camel_case


def data_model_factory(class_type, json_resp):
    for class_name, camel_case_parameters in json_resp.items():
        if class_name.lower() in class_type.__name__.lower():
            snake_case_parameters = _convert_json_camel_2_snake(camel_case_parameters)
            return class_type(**snake_case_parameters)
    raise KeyError(class_type.__name__.lower() + ' not in API response' + f'\nResponse was: \n{json.dumps(json_resp)}')


def _camel_case_to_snake_case(name):
    # magic
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def _convert_json_camel_2_snake(camel_case_dict):
    return dict((_camel_case_to_snake_case(key), value) for (key, value) in camel_case_dict.items())
