# python-sesam
A client library for Sesam. You'll need a Sesam account to use this.

## Usage
```python
from sesam import SesamStudentServiceClient
client = SesamStudentServiceClient(username='<username>', password='<password>')
client.get_student(nor_edu_person_lin='25faeebb-5810-4484-a69c-960d1b77a261')
client.get_student(liu_id='oller120')
client.get_student(mifare_id='2043261358')
client.get_student(national_id='19901129xxxx')
```

Returns a `namedtuple`.
