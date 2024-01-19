from functools import partial
import operator
import csv
import os


class Contact:
    VERSION = '4.0'
    FORMAT = "VCFv" + VERSION
    FIELDS = {
        "name": "FN",
        "organisation": "ORG",
        "phone": "TEL;CELL",
        "email": "EMAIL",
        "title": "TITLE",
        "address": "ADR;HOME",
        "birthday": "BDAY"
    }
    REQUIRED_FIELDS = [
        'name',
        'phone'
    ]

    def __init__(self, **info):
        if ('fname' in info) or ('firstname' in info) or ('first_name' in info):
            info['name'] = info['fname']
        if ('lname' in info) or ('lastname' in info) or ('last_name' in info):
            info['name'] = info['fname']

        if not Contact._check_required_fields(info):
            raise ValueError(f'Not enough information. (necessary fields: {", ".join(Contact.REQUIRED_FIELDS)})')

        self.peresented_fields = Contact._check_peresented_fields(info)
        self.fields = {field: info[field] for field in self.peresented_fields}

    def to_vcf(self):
        result = ['BEGIN:VCARD', f'VERSION:{Contact.VERSION}']
        for field, value in self.fields.items():
            if field == 'name':
                parts = value.split()
                result.append(f"N:{';'.join(parts) + ';'*(5-len(parts))}")
            result.append(f"{Contact.FIELDS[field]}:{value}")
        result.append('END:VCARD')
        return '\n'.join(result)

    @classmethod
    def _check_peresented_fields(cls, fields):
        peresented_fields = []
        for field in Contact.FIELDS:
            if field in fields:
                peresented_fields.append(field)
        return peresented_fields

    @classmethod
    def _check_required_fields(cls, fields):
        for field in Contact.REQUIRED_FIELDS:
            if field not in fields:
                return False
        return True

    def _represent_fields(self):
        return ', '.join(f"{k}={v}" for k, v in self.fields.items())

    def __repr__(self):
        return f"Contact({self._represent_fields()})"


def pad(array, length, fill='', first=False):
    padding = [fill] * (length - len(array))
    if first:
        return padding + array
    return array + padding

def load_csv(path):
    with open(path, newline='') as handler:
        return list(csv.reader(handler))


INPUT_PATH = 'contacts.csv'
OUTPUT_PATH = 'contacts.vcf'
AUTO_NAME = True
NAME_PREFIX = 'P'
FIX_PHONE = True
PHONE_PREFIX = '+98'


if __name__ == '__main__':
    if not os.path.exists(INPUT_PATH) or not os.path.isfile(INPUT_PATH):
        raise FileExistsError(f"File <{INPUT_PATH}> is not a valid file!")
    if os.path.exists(OUTPUT_PATH) and input(f'The output file already exists! <{OUTPUT_PATH}> Are you sure to continue (y/n)? ').lower() != 'y':
        exit()

    content = load_csv(INPUT_PATH)
    header = content.pop(0)
    header = list(map(operator.methodcaller('lower'), header))
    content = list(map(partial(pad, length=len(header)), content))

    if AUTO_NAME and ('name' in header):
        raise RuntimeError("<Auto-Name> is on, but you already have 'name' in header!")
    elif AUTO_NAME:
        header.append('name')
        for i in range(len(content)):
            content[i].append(NAME_PREFIX + str(i+1))
    elif not Contact._check_required_fields(header):
        raise ValueError(f"Invalid header!")

    if FIX_PHONE:
        idx = header.index('phone')
        for i in range(len(content)):
            content[i][idx] = PHONE_PREFIX + content[i][idx]

    contacts = []
    for row in content:
        contacts.append(Contact(**dict(zip(header, row))))

    formatted_vcf = '\n'.join(contact.to_vcf() for contact in contacts)
    with open(OUTPUT_PATH, 'w') as handler:
        handler.write(formatted_vcf)

    print(f'The contacts were exported in <{OUTPUT_PATH}> successfully!')
    print('Added Contacts:', len(contacts))
