from functools import partial
import operator
import time
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

def path_splitter(path):
    parent, filename = os.path.split(path)
    basename, extension = os.path.splitext(filename)
    return parent, basename, extension

def print_figlet(delay=.2):
    for line in FIGLET.splitlines():
        print(line)
        time.sleep(delay)


INPUT_PATH = None
OUTPUT_PATH = None
AUTO_NAME = None  # add 'name' in header by counting. P1,P2,P3
NAME_PREFIX = None
FIX_PHONE = None  # add a prefix to numbers
PHONE_PREFIX = None
FIGLET = '''\n
   _____                 ____
  / ____|               |  __|
 | (___  _ _ __   __ _  | |__ 
  \___ \| | '_ \ / _` | |  __|
  ____) | | | | | (_| |_| |  
 |_____/|_|_| |_|\__,_(_)_| 
\n\n'''


if __name__ == '__main__':
    INPUT_PATH = input('Enter desired csv file: ')
    if not INPUT_PATH.endswith('.csv'):
        INPUT_PATH += '.csv'
    OUTPUT_PATH = os.path.join(*path_splitter(INPUT_PATH)[:2]) + '.vcf'
    if not os.path.exists(INPUT_PATH):
        raise FileExistsError(f"File <{INPUT_PATH}> is not a valid file!")
    if os.path.exists(OUTPUT_PATH) and input(f'The output file already exists! <{OUTPUT_PATH}> Are you sure to continue (y/n)? ').lower() != 'y':
        exit()

    if input('Would you like to auto-name? (y/n) ').lower() == 'y':
        AUTO_NAME = True
        NAME_PREFIX = input('What prefix you like for names? ')
    else:
        AUTO_NAME = False

    if input('Would you like to fix-phones? (y/n) ').lower() == 'y':
        FIX_PHONE = True
        PHONE_PREFIX = input('What prefix you like for phones? ')
    else:
        FIX_PHONE = False

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

    # validate header after adding 'name' if needed
    if not Contact._check_required_fields(header):
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

    print_figlet()
    time.sleep(1)
    input('Press <enter> to exit...')
