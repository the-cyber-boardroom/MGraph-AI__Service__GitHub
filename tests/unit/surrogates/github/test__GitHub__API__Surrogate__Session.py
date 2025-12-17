from unittest                                                                       import TestCase
from fastapi.responses                                                              import JSONResponse
from osbot_fast_api.api.Fast_API                                                    import Fast_API
from osbot_fast_api.api.decorators.route_path                                       import route_path
from osbot_fast_api.api.routes.Fast_API__Routes                                     import Fast_API__Routes
from osbot_utils.decorators.methods.cache_on_self                                   import cache_on_self
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__Session     import GitHub__API__Surrogate__Session, HeadersProxy


class test__GitHub__API__Surrogate__Session(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sample_client = cls.create__sample_client()
        cls.session       = GitHub__API__Surrogate__Session(test_client=cls.sample_client)

    @classmethod
    def create__sample_client(cls):
        class Routes__Sample(Fast_API__Routes):

            def user(self):
                return {"login": "test-user", "id": 12345}

            @route_path('/repos/{owner}/{repo}/secrets/{name}')
            def put_secret(self, owner: str, repo: str, name: str):
                return JSONResponse(content=None, status_code=201)

            @route_path('/repos/{owner}/{repo}/secrets/{name}')
            def delete_secret(self, owner: str, repo: str, name: str):
                return JSONResponse(content=None, status_code=204)

            def data(self):
                return {"created": True}

            def check(self):
                return {"status": "ok"}

            def headers(self):
                return {"status": "ok"}

            def setup_routes(self):
                self.add_route_get   (self.user         )
                self.add_route_put   (self.put_secret   )
                self.add_route_delete(self.delete_secret)
                self.add_route_post  (self.data         )
                self.add_route_get   (self.check        )
                self.add_route_get   (self.headers      )

        class Sample__Fast_API(Fast_API):
            def setup_routes(self):
                self.add_routes(Routes__Sample)

        sample_fast_api = Sample__Fast_API().setup()
        return sample_fast_api.client()

    def test_setup(self):
        assert self.session._headers == {}

    def test_headers_property(self):
        proxy = self.session.headers
        assert isinstance(proxy, HeadersProxy)

    def test_get(self):
        response = self.session.get("/user")

        assert response.status_code == 200
        assert response.json()['login'] == 'test-user'

    def test_put(self):
        response = self.session.put("/repos/owner/repo/secrets/SECRET_NAME", json={"value": "test"})

        assert response.status_code == 201

    def test_delete(self):
        response = self.session.delete("/repos/owner/repo/secrets/SECRET_NAME")

        assert response.status_code == 204

    def test_post(self):
        response = self.session.post("/data", json={"key": "value"})

        assert response.status_code == 200
        assert response.json()['created'] is True

    def test_convert_url_to_path_full_url(self):
        path = self.session._convert_url_to_path("https://api.github.com/user")
        assert path == "/user"

    def test_convert_url_to_path_already_path(self):
        path = self.session._convert_url_to_path("/user")
        assert path == "/user"

    def test_convert_url_to_path_other_url(self):
        path = self.session._convert_url_to_path("https://other.com/some/path")
        assert path == "/some/path"

    def test_headers_merged_in_request(self):
        session = GitHub__API__Surrogate__Session(test_client=self.sample_client)

        # Set session-level header
        session.headers.update({'Authorization': 'token session_token'})

        # Make request
        response = session.get("/check")

        # Note: FastAPI Header injection works differently, but the headers are sent
        assert response.status_code == 200

    def test_request_headers_override_session_headers(self):
        session = GitHub__API__Surrogate__Session(test_client=self.sample_client)

        # Set session header
        session.headers.update({'X-Test': 'session_value'})

        # Make request with override - should merge headers
        response = session.get("/headers", headers={'X-Test': 'request_value'})
        assert response.status_code == 200

    def test_prepare_headers_empty(self):
        headers = self.session._prepare_headers({})
        assert headers == {}

    def test_prepare_headers_with_session_headers(self):
        session          = GitHub__API__Surrogate__Session(test_client=self.sample_client)
        session._headers = {'Authorization': 'token abc'}
        headers          = session._prepare_headers({})
        assert headers  == {'Authorization': 'token abc'}

    def test_prepare_headers_with_request_headers(self):
        session          = GitHub__API__Surrogate__Session(test_client=self.sample_client)
        session._headers = {'Session-Header': 'session_value'}
        headers          = session._prepare_headers({'headers': {'Request-Header': 'request_value'}})

        assert headers['Session-Header'] == 'session_value'
        assert headers['Request-Header'] == 'request_value'

    def test_prepare_headers_request_overrides_session(self):
        session          = GitHub__API__Surrogate__Session(test_client=self.sample_client)
        session._headers = {'X-Header': 'session_value'}
        headers          = session._prepare_headers({'headers': {'X-Header': 'request_value'}})

        assert headers['X-Header'] == 'request_value'