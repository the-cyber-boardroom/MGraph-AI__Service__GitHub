from osbot_fast_api.api.Fast_API_Routes import Fast_API_Routes

from mgraph_ai_service_github.service.auth.Service__Auth import Service__Auth

TAG__ROUTES_AUTH                  = 'auth'
ROUTES_PATHS__AUTH                = [ f'/{TAG__ROUTES_AUTH}/public-key'  ,
                                      f'/{TAG__ROUTES_AUTH}/test'        ,
                                      f'/{TAG__ROUTES_AUTH}/test-api-key']

class Routes__Auth(Fast_API_Routes):
    service_auth : Service__Auth

    def public_key(self):
        return self.service_auth.public_key()

    def test(self):
        return self.service_auth.test()

    def test_api_key(self):
        return self.service_auth.test_api_key()

    def setUp_routes(self):
        self.add_route_get(self.public_key  )
        self.add_route_get(self.test        )
        self.add_route_get(self.test_api_key)

