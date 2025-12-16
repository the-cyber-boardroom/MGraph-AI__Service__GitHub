from typing                                                                                    import Dict, Any
from fastapi                                                                                   import Header
from fastapi.responses                                                                         import JSONResponse
from osbot_fast_api.api.decorators.route_path                                                  import route_path
from mgraph_ai_service_github.surrogates.github.routes.Routes__GitHub__Base                    import Routes__GitHub__Base


class Routes__GitHub__User(Routes__GitHub__Base):                               # Routes for /user and /rate_limit endpoints

    def user(self, authorization: str = Header(None)                            # GET /user - Get authenticated user
             ) -> Dict[str, Any]:
        valid, error_response, pat = self.auth_error_response(authorization)
        if not valid:
            return error_response

        user = self.pats.get_user(pat)
        if not user:
            return JSONResponse(content=self._error_response("Bad credentials", 401), status_code=401)

        return user.to_github_response()

    @route_path('/rate_limit')
    def rate_limit(self, authorization: str = Header(None)                      # GET /rate_limit - Get rate limit status
                   ) -> Dict[str, Any]:
        valid, error_response, pat = self.auth_error_response(authorization)
        if not valid:
            return error_response

        rate_limit = self.state.get_rate_limit(pat)
        return rate_limit.to_github_response()

    def setup_routes(self):                                                     # Register routes
        self.add_route_get(self.user      )
        self.add_route_get(self.rate_limit)
        return self
