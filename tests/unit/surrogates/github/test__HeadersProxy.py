from unittest                                                                      import TestCase
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__Session    import GitHub__API__Surrogate__Session, HeadersProxy, SurrogateResponse

class test__HeadersProxy(TestCase):

    def test_update(self):
        session = GitHub__API__Surrogate__Session()

        proxy = session.headers
        proxy.update({'Authorization': 'token abc123'})

        assert session._headers['Authorization'] == 'token abc123'

    def test_setitem(self):
        session = GitHub__API__Surrogate__Session()

        proxy = session.headers
        proxy['X-Custom-Header'] = 'custom_value'

        assert session._headers['X-Custom-Header'] == 'custom_value'

    def test_getitem(self):
        session = GitHub__API__Surrogate__Session()
        session._headers['Test-Key'] = 'test_value'

        proxy = session.headers
        assert proxy['Test-Key'] == 'test_value'

    def test_get(self):
        session = GitHub__API__Surrogate__Session()
        session._headers['Existing'] = 'value'

        proxy = session.headers
        assert proxy.get('Existing')      == 'value'
        assert proxy.get('Missing')       is None
        assert proxy.get('Missing', 'default') == 'default'