from typing                                                                                    import Dict, Any
from fastapi                                                                                   import Header, Request
from fastapi.responses                                                                         import JSONResponse
from osbot_fast_api.api.decorators.route_path                                                  import route_path
from mgraph_ai_service_github.surrogates.github.routes.Routes__GitHub__Base                    import Routes__GitHub__Base


class Routes__GitHub__Env_Secrets(Routes__GitHub__Base):                        # Routes for environment secrets endpoints

    @route_path('/repos/{owner}/{repo}/environments/{environment}/secrets/public-key')
    def get_env_public_key(self, owner         : str              ,             # GET /repos/{owner}/{repo}/environments/{environment}/secrets/public-key
                                 repo          : str              ,
                                 environment   : str              ,
                                 authorization : str = Header(None)
                           ) -> Dict[str, Any]:
        valid, error_response, pat = self.auth_error_response(authorization)
        if not valid:
            return error_response

        can_read, error_response = self.repo_read_error_response(pat)
        if not can_read:
            return error_response

        if not self.state.repo_exists(owner, repo):
            return self.not_found_response()

        if not self.state.environment_exists(owner, repo, environment):
            return self.not_found_response()

        public_key = self.keys.get_env_public_key(owner, repo, environment)
        self.state.set_public_key(self.keys.scope_id_for_env(owner, repo, environment), public_key)

        return public_key.to_github_response()

    @route_path('/repos/{owner}/{repo}/environments/{environment}/secrets')
    def list_env_secrets(self, owner         : str              ,               # GET /repos/{owner}/{repo}/environments/{environment}/secrets
                               repo          : str              ,
                               environment   : str              ,
                               authorization : str = Header(None)
                         ) -> Dict[str, Any]:
        valid, error_response, pat = self.auth_error_response(authorization)
        if not valid:
            return error_response

        can_read, error_response = self.repo_read_error_response(pat)
        if not can_read:
            return error_response

        if not self.state.repo_exists(owner, repo):
            return self.not_found_response()

        if not self.state.environment_exists(owner, repo, environment):
            return self.not_found_response()

        secrets      = self.state.list_env_secrets(owner, repo, environment)
        secrets_list = [s.to_github_response() for s in secrets]

        return dict(total_count = len(secrets_list) ,
                    secrets     = secrets_list      )

    @route_path('/repos/{owner}/{repo}/environments/{environment}/secrets/{secret_name}')
    def get_env_secret(self, owner         : str              ,                 # GET /repos/{owner}/{repo}/environments/{environment}/secrets/{secret_name}
                             repo          : str              ,
                             environment   : str              ,
                             secret_name   : str              ,
                             authorization : str = Header(None)
                       ) -> Dict[str, Any]:
        valid, error_response, pat = self.auth_error_response(authorization)
        if not valid:
            return error_response

        can_read, error_response = self.repo_read_error_response(pat)
        if not can_read:
            return error_response

        if not self.state.repo_exists(owner, repo):
            return self.not_found_response()

        if not self.state.environment_exists(owner, repo, environment):
            return self.not_found_response()

        secret = self.state.get_env_secret(owner, repo, environment, secret_name)
        if not secret:
            return self.not_found_response()

        return secret.to_github_response()

    @route_path('/repos/{owner}/{repo}/environments/{environment}/secrets/{secret_name}')
    async def put_env_secret(self, owner         : str              ,           # PUT /repos/{owner}/{repo}/environments/{environment}/secrets/{secret_name}
                                   repo          : str              ,
                                   environment   : str              ,
                                   secret_name   : str              ,
                                   request       : Request          ,
                                   authorization : str = Header(None)
                             ) -> JSONResponse:
        valid, error_response, pat = self.auth_error_response(authorization)
        if not valid:
            return error_response

        can_write, error_response = self.repo_write_error_response(pat)
        if not can_write:
            return error_response

        if not self.state.repo_exists(owner, repo):
            return self.not_found_response()

        if not self.state.environment_exists(owner, repo, environment):
            return self.not_found_response()

        body            = await request.json()
        encrypted_value = body.get('encrypted_value', '')
        key_id          = body.get('key_id', '')

        existing = self.state.get_env_secret(owner, repo, environment, secret_name)

        self.state.set_env_secret(owner, repo, environment, secret_name, encrypted_value, key_id)

        if existing:
            return JSONResponse(content=None, status_code=204)
        else:
            return JSONResponse(content=None, status_code=201)

    @route_path('/repos/{owner}/{repo}/environments/{environment}/secrets/{secret_name}')
    def delete_env_secret(self, owner         : str              ,              # DELETE /repos/{owner}/{repo}/environments/{environment}/secrets/{secret_name}
                                repo          : str              ,
                                environment   : str              ,
                                secret_name   : str              ,
                                authorization : str = Header(None)
                          ) -> JSONResponse:
        valid, error_response, pat = self.auth_error_response(authorization)
        if not valid:
            return error_response

        can_write, error_response = self.repo_write_error_response(pat)
        if not can_write:
            return error_response

        if not self.state.repo_exists(owner, repo):
            return self.not_found_response()

        if not self.state.environment_exists(owner, repo, environment):
            return self.not_found_response()

        deleted = self.state.delete_env_secret(owner, repo, environment, secret_name)
        if not deleted:
            return self.not_found_response()

        return JSONResponse(content=None, status_code=204)

    def setup_routes(self):                                                     # Register routes
        self.add_route_get   (self.get_env_public_key)
        self.add_route_get   (self.list_env_secrets  )
        self.add_route_get   (self.get_env_secret    )
        self.add_route_put   (self.put_env_secret    )
        self.add_route_delete(self.delete_env_secret )
        return self
