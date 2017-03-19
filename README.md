# python-sesam
A client library for Sesam. You'll need a Sesam account to use this.

## Installation
```bash
pip install sesam
```

## Usage
```python
from sesam import SesamStudentServiceClient
client = SesamStudentServiceClient(username='<username>', password='<password>')
client.get_student(iso_id='9752268587108')
client.get_student(liu_id='oller120')
client.get_student(mifare_id='2043261358')
client.get_student(nor_edu_person_lin='25faeebb-5810-4484-a69c-960d1b77a261')
client.get_student(nor_edu_person_nin='19901129xxxx')
```

Response is a namedtuple:
```python
SesamStudent(liu_id='oller120',
             email='oller120@student.liu.se',
             nor_edu_person_lin=UUID('25faeebb-5810-4484-a69c-960d1b77a261'),
             liu_lin=UUID('bcbb39b7-5508-43a3-8c85-f835b1e5f9af'),
             full_name='Olle Vidner',
             first_name='Olle',
             last_name='Vidner',
             main_union='LinTek',
             student_union='M',
             edu_person_affiliations=('alum',
                                      'member',
                                      'student'),
             edu_person_scoped_affiliations=('alum@liu.se',
                                             'member@ida.liu.se',
                                             'member@iei.liu.se',
                                             'member@isy.liu.se',
                                             'member@itn.liu.se',
                                             'member@liu.se',
                                             'member@mai.liu.se',
                                             'member@mecenat.se',
                                             'member@tfk.liu.se',
                                             'member@traveldiscount.se',
                                             'student@ida.liu.se',
                                             'student@iei.liu.se',
                                             'student@isy.liu.se',
                                             'student@itn.liu.se',
                                             'student@liu.se',
                                             'student@mai.liu.se',
                                             'student@tfk.liu.se'),
             edu_person_primary_affiliation='student')
```

## Important considerations
* Card numbers and national ID (norEduPersonNIN) are never returned due to privacy 
considerations.
* `nor_edu_person_lin` (norEduPersonLIN) is a persistent and universal 
identifier used by many other services. Use this to make integrations with other 
services rather than LiU IDs, if possible. LiU IDs *may* change.  
* The `student_union` field is *not* a reliable indicator for section 
membership – not all sections register members through Sture/Sesam.
