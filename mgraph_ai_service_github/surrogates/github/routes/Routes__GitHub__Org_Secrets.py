from typing                                                                                    import Dict, Any
from fastapi                                                                                   import Header, Request
from fastapi.responses                                                                         import JSONResponse
from osbot_fast_api.api.decorators.route_path                                                  import route_path
from mgraph_ai_service_github.surrogates.github.routes.Routes__GitHub__Base                    import Routes__GitHub__Base


class Routes__GitHub__Org_Secrets(Routes__GitHub__Base):                        # Routes for organization secrets endpoints

    @route_path('/orgs/{org}/actions/secrets/public-key')
    def get_org_public_key(self, org           : str              ,             # GET /orgs/{org}/actions/secrets/public-key
                                 authorization : str = Header(None)
                           ) -> Dict[str, Any]:
        valid, error_response, pat = self.auth_error_response(authorization)
        if not valid:
            return error_response

        can_admin, error_response = self.org_admin_error_response(pat)
        if not can_admin:
            return error_response

        if not self.state.org_exists(org):
            return self.not_found_response()

        public_key = self.keys.get_org_public_key(org)
        self.state.set_public_key(self.keys.scope_id_for_org(org), public_key)

        return public_key.to_github_response()

    @route_path('/orgs/{org}/actions/secrets')
    def list_org_secrets(self, org           : str              ,               # GET /orgs/{org}/actions/secrets
                               authorization : str = Header(None)
                         ) -> Dict[str, Any]:
        valid, error_response, pat = self.auth_error_response(authorization)
        if not valid:
            return error_response

        can_admin, error_response = self.org_admin_error_response(pat)
        if not can_admin:
            return error_response

        if not self.state.org_exists(org):
            return self.not_found_response()

        secrets      = self.state.list_org_secrets(org)
        secrets_list = [s.to_github_response() for s in secrets]

        return dict(total_count = len(secrets_list) ,
                    secrets     = secrets_list      )

    @route_path('/orgs/{org}/actions/secrets/{secret_name}')
    def get_org_secret(self, org           : str              ,                 # GET /orgs/{org}/actions/secrets/{secret_name}
                             secret_name   : str              ,
                             authorization : str = Header(None)
                       ) -> Dict[str, Any]:
        valid, error_response, pat = self.auth_error_response(authorization)
        if not valid:
            return error_response

        can_admin, error_response = self.org_admin_error_response(pat)
        if not can_admin:
            return error_response

        if not self.state.org_exists(org):
            return self.not_found_response()

        secret = self.state.get_org_secret(org, secret_name)
        if not secret:
            return self.not_found_response()

        return secret.to_github_response()

    @route_path('/orgs/{org}/actions/secrets/{secret_name}')
    async def put_org_secret(self, org           : str              ,           # PUT /orgs/{org}/actions/secrets/{secret_name}
                                   secret_name   : str              ,
                                   request       : Request          ,
                                   authorization : str = Header(None)
                             ) -> JSONResponse:
        valid, error_response, pat = self.auth_error_response(authorization)
        if not valid:
            return error_response

        can_admin, error_response = self.org_admin_error_response(pat)
        if not can_admin:
            return error_response

        if not self.state.org_exists(org):
            return self.not_found_response()

        body            = await request.json()
        encrypted_value = body.get('encrypted_value', '')
        key_id          = body.get('key_id', '')
        visibility      = body.get('visibility', 'private')

        existing = self.state.get_org_secret(org, secret_name)

        self.state.set_org_secret(org, secret_name, encrypted_value, key_id, visibility)

        if existing:
            return JSONResponse(content=None, status_code=204)
        else:
            return JSONResponse(content=None, status_code=201)

    @route_path('/orgs/{org}/actions/secrets/{secret_name}')
    def delete_org_secret(self, org           : str              ,              # DELETE /orgs/{org}/actions/secrets/{secret_name}
                                secret_name   : str              ,
                                authorization : str = Header(None)
                          ) -> JSONResponse:
        valid, error_response, pat = self.auth_error_response(authorization)
        if not valid:
            return error_response

        can_admin, error_response = self.org_admin_error_response(pat)
        if not can_admin:
            return error_response

        if not self.state.org_exists(org):
            return self.not_found_response()

        deleted = self.state.delete_org_secret(org, secret_name)
        if not deleted:
            return self.not_found_response()

        return JSONResponse(content=None, status_code=204)

    def setup_routes(self):                                                     # Register routes
        self.add_route_get   (self.get_org_public_key)
        self.add_route_get   (self.list_org_secrets  )
        self.add_route_get   (self.get_org_secret    )
        self.add_route_put   (self.put_org_secret    )
        self.add_route_delete(self.delete_org_secret )
        return self
