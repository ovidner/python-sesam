import re
import uuid
from binascii import hexlify
from os import urandom

import pytest
import responses
from lxml import etree, objectify

import sesam

STUDENT_SERVICE_ENDPOINT_URL = 'https://service.integration.it.liu.se/StudentService/2.0/StudentService.svc/basic'

FULL_REQUEST_XML = """<?xml version='1.0' encoding='utf-8'?>
<soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/">
    <soap-env:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
        <wsa:Action>http://service.integration.it.liu.se/StudentService/2.0/IStudentService/GetStudent</wsa:Action>
        <wsa:MessageID>urn:uuid:80361e99-b260-4cac-8604-f8ff08d635a8</wsa:MessageID>
        <wsa:To>https://service.integration.it.liu.se/StudentService/2.0/StudentService.svc/basic</wsa:To>
        <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
            <wsse:UsernameToken>
                <wsse:Username>{username}</wsse:Username>
                <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{password}</wsse:Password>
            </wsse:UsernameToken>
        </wsse:Security>
    </soap-env:Header>
    <soap-env:Body>
        <ns0:GetStudent xmlns:ns0="http://service.integration.it.liu.se/StudentService/2.0">
            <ns0:Request>
                <ns1:Identity xmlns:ns1="http://service.integration.it.liu.se/EmployeeService/2.1/Contract">
                    <ns2:IsoNumber xmlns:ns2="http://service.integration.it.liu.se/ViewModels">1234567890123456</ns2:IsoNumber>
                    <ns3:LiUId xmlns:ns3="http://service.integration.it.liu.se/ViewModels">oller120</ns3:LiUId>
                    <ns4:MifareNumber xmlns:ns4="http://service.integration.it.liu.se/ViewModels">2043261358</ns4:MifareNumber>
                    <ns5:norEduPersonLIN xmlns:ns5="http://service.integration.it.liu.se/ViewModels">25faeebb-5810-4484-a69c-960d1b77a261</ns5:norEduPersonLIN>
                    <ns6:norEduPersonNIN xmlns:ns6="http://service.integration.it.liu.se/ViewModels">199011290000</ns6:norEduPersonNIN>
                </ns1:Identity>
            </ns0:Request>
        </ns0:GetStudent>
    </soap-env:Body>
</soap-env:Envelope>
"""


FOUND_RESPONSE_XML = """<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" xmlns:u="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
    <s:Header>
        <ActivityId CorrelationId="9fb4a4ae-19fd-43d1-b1ae-89bbb5036595" xmlns="http://schemas.microsoft.com/2004/09/ServiceModel/Diagnostics">00000000-0000-0000-0000-000000000000</ActivityId>
        <o:Security s:mustUnderstand="1" xmlns:o="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
            <u:Timestamp u:Id="_0">
                <u:Created>2017-10-03T23:11:21.956Z</u:Created>
                <u:Expires>2017-10-03T23:16:21.956Z</u:Expires>
            </u:Timestamp>
        </o:Security>
    </s:Header>
    <s:Body>
        <GetStudentResponse xmlns="http://service.integration.it.liu.se/StudentService/2.0">
            <GetStudentResult xmlns:a="http://service.integration.it.liu.se/EmployeeService/2.1/Contract" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
                <a:Student xmlns:b="http://service.integration.it.liu.se/EmployeeService/2.1/ViewModels">
                    <b:DisplayName>Olle Vidner</b:DisplayName>
                    {email}
                    <b:GivenName>Olle</b:GivenName>
                    <b:LiUId>oller120</b:LiUId>
                    <b:LiULIN>bcbb39b7-5508-43a3-8c85-f835b1e5f9af</b:LiULIN>
                    {main_union}
                    {student_union}
                    <b:SurName>Vidner</b:SurName>
                    <b:eduPersonAffiliations xmlns:c="http://schemas.microsoft.com/2003/10/Serialization/Arrays">
                        <c:string>member</c:string>
                        <c:string>student</c:string>
                        <c:string>alum</c:string>
                    </b:eduPersonAffiliations>
                    <b:eduPersonPrimaryAffiliation>student</b:eduPersonPrimaryAffiliation>
                    <b:eduPersonScopedAffiliations xmlns:c="http://schemas.microsoft.com/2003/10/Serialization/Arrays">
                        <c:string>member@liu.se</c:string>
                        <c:string>student@liu.se</c:string>
                        <c:string>member@mecenat.se</c:string>
                        <c:string>alum@liu.se</c:string>
                        <c:string>student@ida.liu.se</c:string>
                        <c:string>member@ida.liu.se</c:string>
                        <c:string>student@mai.liu.se</c:string>
                        <c:string>member@mai.liu.se</c:string>
                        <c:string>student@iei.liu.se</c:string>
                        <c:string>member@iei.liu.se</c:string>
                        <c:string>student@tfk.liu.se</c:string>
                        <c:string>member@tfk.liu.se</c:string>
                        <c:string>student@isy.liu.se</c:string>
                        <c:string>member@isy.liu.se</c:string>
                        <c:string>member@traveldiscount.se</c:string>
                    </b:eduPersonScopedAffiliations>
                    <b:norEduPersonLIN>25faeebb-5810-4484-a69c-960d1b77a261</b:norEduPersonLIN>
                </a:Student>
            </GetStudentResult>
        </GetStudentResponse>
    </s:Body>
</s:Envelope>
"""

NOT_FOUND_RESPONSE_XML = """<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" xmlns:u="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
    <s:Header>
        <o:Security s:mustUnderstand="1" xmlns:o="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
            <u:Timestamp u:Id="_0">
                <u:Created>2017-10-06T15:35:26.509Z</u:Created>
                <u:Expires>2017-10-06T15:40:26.509Z</u:Expires>
            </u:Timestamp>
        </o:Security>
    </s:Header>
    <s:Body>
        <s:Fault>
            <faultcode>s:Client</faultcode>
            <faultstring xml:lang="sv-SE">
                Error in GetStudent&#xD;
InnerException: Could not find Student in database
            </faultstring>
        </s:Fault>
    </s:Body>
</s:Envelope>
"""


def normalized_xml_representation(xml):
    if isinstance(xml, str):
        xml = xml.encode('utf-8')
    # If we can find a MessageID with a UUID in it, reset it to something
    # deterministic. Why not Zoidberg?
    xml = re.sub(
        rb'<wsa:MessageID>urn:uuid:[0-9A-Fa-f-]{36}</wsa:MessageID>',
        b'<wsa:MessageID>urn:uuid:zoidberg</wsa:MessageID>',
        xml
    )
    return objectify.dump(etree.XML(xml))


def xml_equal(a, b):
    return normalized_xml_representation(a) == normalized_xml_representation(b)


@pytest.fixture
def random_string():
    def create(length):
        # Returns a random hex string, `length` characters long.
        return hexlify(urandom(length // 2 + (length % 2 > 0)))[0:length].decode()
    return create


@pytest.fixture
def username(random_string):
    return f'{random_string(8)}@ad.liu.se'


@pytest.fixture
def password(random_string):
    return random_string(16)


@pytest.fixture
def full_request_xml(username, password):
    return FULL_REQUEST_XML.format(username=username, password=password)


@pytest.fixture
def client(username, password):
    return sesam.StudentServiceClient(username=username, password=password)


@pytest.mark.parametrize('call_kwargs', [
    dict(
        iso_id='1234567890123456',
        liu_id='oller120',
        mifare_id='2043261358',
        nor_edu_person_lin='25faeebb-5810-4484-a69c-960d1b77a261',
        nor_edu_person_nin='199011290000'
    ),
    dict(
        iso_id='0001234567890123456',
        liu_id='oller120',
        mifare_id='002043261358',
        nor_edu_person_lin='25faeebb-5810-4484-a69c-960d1b77a261',
        nor_edu_person_nin='199011290000'
    ),
    dict(
        iso_id=1234567890123456,
        liu_id='oller120',
        mifare_id=2043261358,
        nor_edu_person_lin=uuid.UUID('25faeebb-5810-4484-a69c-960d1b77a261'),
        nor_edu_person_nin=199011290000
    ),
])
@pytest.mark.parametrize(('response_status', 'response_xml', 'expected_result'), [
    (
        200,
        FOUND_RESPONSE_XML.format(
            email='<b:EmailAddress i:nil="true"/>',
            main_union='<b:MainUnion i:nil="true"/>',
            student_union='<b:StudentUnion i:nil="true"/>'
        ),
        sesam.Student(
            full_name='Olle Vidner',
            first_name='Olle',
            last_name='Vidner',
            liu_id='oller120',
            email='oller120@student.liu.se',
            nor_edu_person_lin=uuid.UUID('25faeebb-5810-4484-a69c-960d1b77a261'),
            liu_lin=uuid.UUID('bcbb39b7-5508-43a3-8c85-f835b1e5f9af'),
            main_union=None,
            student_union=None,
            edu_person_affiliations=frozenset({'alum', 'member', 'student'}),
            edu_person_scoped_affiliations=frozenset({
                'alum@liu.se',
                'member@ida.liu.se',
                'member@iei.liu.se',
                'member@isy.liu.se',
                'member@liu.se',
                'member@mai.liu.se',
                'member@mecenat.se',
                'member@tfk.liu.se',
                'member@traveldiscount.se',
                'student@ida.liu.se',
                'student@iei.liu.se',
                'student@isy.liu.se',
                'student@liu.se',
                'student@mai.liu.se',
                'student@tfk.liu.se'
            }),
            edu_person_primary_affiliation='student',
        )
    ),
    (
        200,
        FOUND_RESPONSE_XML.format(
            email='<b:EmailAddress>oller120@student.liu.se</b:EmailAddress>',
            main_union='<b:MainUnion>LinTek</b:MainUnion>',
            student_union='<b:StudentUnion>M</b:StudentUnion>'
        ),
        sesam.Student(
            full_name='Olle Vidner',
            first_name='Olle',
            last_name='Vidner',
            liu_id='oller120',
            email='oller120@student.liu.se',
            nor_edu_person_lin=uuid.UUID('25faeebb-5810-4484-a69c-960d1b77a261'),
            liu_lin=uuid.UUID('bcbb39b7-5508-43a3-8c85-f835b1e5f9af'),
            main_union='LinTek',
            student_union='M',
            edu_person_affiliations=frozenset({'alum', 'member', 'student'}),
            edu_person_scoped_affiliations=frozenset({
                'alum@liu.se',
                'member@ida.liu.se',
                'member@iei.liu.se',
                'member@isy.liu.se',
                'member@liu.se',
                'member@mai.liu.se',
                'member@mecenat.se',
                'member@tfk.liu.se',
                'member@traveldiscount.se',
                'student@ida.liu.se',
                'student@iei.liu.se',
                'student@isy.liu.se',
                'student@liu.se',
                'student@mai.liu.se',
                'student@tfk.liu.se'
            }),
            edu_person_primary_affiliation='student',
        )
    ),
    (
        500,
        NOT_FOUND_RESPONSE_XML,
        sesam.StudentNotFound()
    )
])
def test_full_request(client, full_request_xml, response_status, response_xml, call_kwargs, expected_result):
    def callback(request):
        assert xml_equal(request.body, full_request_xml)
        return response_status, {}, response_xml

    def make_request():
        return client.get_student(**call_kwargs)

    with responses.RequestsMock() as rm:
        rm.add_callback(
            responses.POST,
            STUDENT_SERVICE_ENDPOINT_URL,
            callback
        )

        if issubclass(type(expected_result), Exception):
            with pytest.raises(type(expected_result)):
                make_request()
        else:
            result = make_request()
            assert result == expected_result
