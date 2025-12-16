import pytest
from unittest                                                                       import TestCase
from fastapi.responses                                                              import JSONResponse
from osbot_fast_api.api.Fast_API                                                    import Fast_API
from osbot_fast_api.api.routes.Fast_API__Routes                                     import Fast_API__Routes
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__Session     import SurrogateResponse


class test__SurrogateResponse(TestCase):

    def client(self):
        class Routes__Sample(Fast_API__Routes):
            def success(self):
                return {"status": "ok", "data": [1, 2, 3]}

            def error(self):
                return JSONResponse(content={"error": "not found"}, status_code=404)

            def empty(self):
                return JSONResponse(content=None, status_code=204)

            def setup_routes(self):
                self. add_routes_get(self.success,
                                     self.error  ,
                                     self.empty  )

        class Sample__Fast_API(Fast_API):
            def setup_routes(self):
                self.add_routes(Routes__Sample)

        sample_fast_api = Sample__Fast_API().setup()
        sample_client   = sample_fast_api.client()

        return sample_client




    def test_status_code(self):
        response = SurrogateResponse(self.client().get("/success"))
        assert response.status_code == 200

    def test_json(self):
        response = SurrogateResponse(self.client().get("/success"))

        data = response.json()
        assert data['status'] == 'ok'
        assert data['data']   == [1, 2, 3]

    def test_content(self):
        response = SurrogateResponse(self.client().get("/success"))

        assert b'status' in response.content

    def test_text(self):
        response = SurrogateResponse(self.client().get("/success"))

        assert 'status' in response.text

    def test_headers(self):
        response = SurrogateResponse(self.client().get("/success"))
        assert 'content-type' in response.headers

    def test_raise_for_status_success(self):
        response = SurrogateResponse(self.client().get("/success"))

        # Should not raise
        response.raise_for_status()

    def test_raise_for_status_error(self):
        response = SurrogateResponse(self.client().get("/error"))

        with pytest.raises(Exception) as exc_info:
            response.raise_for_status()

        assert "404" in str(exc_info.value)
