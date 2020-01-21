import random
import string

def create_token():
    """Returns a random 64-len string"""
    alphabet = []
    alphabet.extend(string.ascii_letters)
    alphabet.extend(string.digits)
    return ''.join(random.choice(alphabet) for i in range(64))

def dict_keys_to_camel_case(dictionary):
    """Converts all keys in provided dict to camelCase"""
    converted_dict = {}
    for key, value in dictionary.items():
        converted_dict[snake_to_camel_case(key)] = value
    return converted_dict

def snake_to_camel_case(name):
    """snake_case String to camelCasse"""
    name = list(name)
    while "_" in name:
        idx = name.index("_")
        if idx + 1 < len(name):
            name[idx + 1] = name[idx + 1].capitalize()
        del name[idx]
    return ''.join(name)

def db_entry_to_dict(table_entry, camel_case=False):
        """As sqlalchemy table entry cant be parsed to json we build a custom converter"""
        attr_dict = {c.name: getattr(table_entry, c.name) for c in table_entry.__table__.columns}
        if camel_case:
            return dict_keys_to_camel_case(attr_dict)
        else:
            return attr_dict

def db_single_element_query(table, arg_dict, element_name):
    """Queries :table: with :arg_dict: as filter"""
    try:
        element = table.query.filter_by(**arg_dict).first()
    except ValueError:
        raise ValueError("Invalid args: {}".format(arg_dict))

    if not element:
        raise ValueError("No such {}".format(element_name))

    return element
