# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
from collections import namedtuple
from os import path

from zeep import Client
from zeep.exceptions import Error as ZeepError
from zeep.wsse import UsernameToken


# I'm not a fan of the idea of fetching an API definition over HTTP just to
# initialize an API client.
DEFAULT_STUDENT_SERVICE_WSDL_URL = (
    'file://{}/wsdl/StudentService_2.0_production.wsdl'.format(
        path.dirname(path.realpath(__file__)))
)
DEFAULT_STUDENT_SERVICE_PORT_NAME = 'BasicHttpBinding_IStudentService'

NOT_FOUND_MESSAGE = 'Could not find Student in database'

# Using a namedtuple gives us immutability and a more defined API for Sesam's
# results than using a plain dict. Still it offers an easy way of mocking
# responses for testing.
SesamStudent = namedtuple('SesamStudent', (
    # Identifiers
    'liu_id',
    'email',
    'nor_edu_person_lin',
    'liu_lin',
    'full_name',
    'first_name',
    'last_name',

    # Affiliations
    'main_union',
    'student_union',
    'edu_person_affiliations',
    'edu_person_scoped_affiliations',
    'edu_person_primary_affiliation'
))


class SesamError(Exception):
    def __init__(self, original_exception=None, *args, **kwargs):
        super(SesamError, self).__init__(*args, **kwargs)
        self.original_exception = original_exception


class SesamStudentNotFound(SesamError):
    def __str__(self):
        return 'Student not found'


class SesamStudentServiceClient(object):
    def __init__(self, username, password,
                 wsdl_url=DEFAULT_STUDENT_SERVICE_WSDL_URL,
                 port_name=DEFAULT_STUDENT_SERVICE_PORT_NAME):
        self.zeep_client = Client(
            wsdl=wsdl_url, port_name=port_name,
            wsse=UsernameToken(username=username, password=password)
        )

    def get_student(self, iso_id=None, liu_id=None, mifare_id=None,
                    nor_edu_person_lin=None, nor_edu_person_nin=None):
        # Removes leading zeros from card numbers
        if iso_id:
            iso_id = str(iso_id).lstrip('0')
        if mifare_id:
            mifare_id = str(mifare_id).lstrip('0')

        try:
            response = self.zeep_client.service.GetStudent(dict(
                Identity=dict(
                    IsoNumber=iso_id,
                    LiUId=liu_id,
                    MifareNumber=mifare_id,
                    norEduPersonLIN=nor_edu_person_lin,
                    norEduPersonNIN=nor_edu_person_nin
                )
            ))
        except ZeepError as exc:
            if NOT_FOUND_MESSAGE in exc.message:
                raise SesamStudentNotFound(original_exception=exc)
            raise SesamError(original_exception=exc)

        return SesamStudent(
            liu_id=response.LiUId,
            email=response.EmailAddress,
            nor_edu_person_lin=uuid.UUID(response.norEduPersonLIN),
            liu_lin=uuid.UUID(response.LiULIN),
            full_name=response.DisplayName,
            first_name=response.GivenName,
            last_name=response.SurName,
            main_union=response.MainUnion,
            student_union=response.StudentUnion,
            edu_person_affiliations=tuple(sorted(
                response.eduPersonAffiliations.string)),
            edu_person_primary_affiliation=response.eduPersonPrimaryAffiliation,
            edu_person_scoped_affiliations=tuple(sorted(
                response.eduPersonScopedAffiliations.string))
        )
