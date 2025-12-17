from typing                                                                                    import Dict, Any
from fastapi                                                                                   import Header, Request
from fastapi.responses                                                                         import JSONResponse
from osbot_fast_api.api.decorators.route_path                                                  import route_path
from mgraph_ai_service_github.surrogates.github.routes.Routes__GitHub__Base                    import Routes__GitHub__Base


class Routes__GitHub__Repo_Secrets(Routes__GitHub__Base):                       # Routes for repository secrets endpoints

    @route_path('/repos/{owner}/{repo}/actions/secrets/public-key')
    def get_repo_public_key(self, owner         : str              ,            # GET /repos/{owner}/{repo}/actions/secrets/public-key
                                  repo          : str              ,
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

        public_key = self.keys.get_repo_public_key(owner, repo)
        self.state.set_public_key(self.keys.scope_id_for_repo(owner, repo), public_key)

        return public_key.to_github_response()

    @route_path('/repos/{owner}/{repo}/actions/secrets')
    def list_repo_secrets(self, owner         : str              ,              # GET /repos/{owner}/{repo}/actions/secrets
                                repo          : str              ,
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

        secrets      = self.state.list_repo_secrets(owner, repo)
        secrets_list = [s.to_github_response() for s in secrets]

        return dict(total_count = len(secrets_list) ,
                    secrets     = secrets_list      )

    @route_path('/repos/{owner}/{repo}/actions/secrets/{secret_name}')
    def get_repo_secret(self, owner         : str              ,                # GET /repos/{owner}/{repo}/actions/secrets/{secret_name}
                              repo          : str              ,
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

        secret = self.state.get_repo_secret(owner, repo, secret_name)
        if not secret:
            return self.not_found_response()

        return secret.to_github_response()

    @route_path('/repos/{owner}/{repo}/actions/secrets/{secret_name}')
    def put_repo_secret(self, owner         : str              ,          # PUT /repos/{owner}/{repo}/actions/secrets/{secret_name}
                             repo           : str              ,
                             secret_name    : str              ,
                             body           : dict ,
                             authorization : str = Header(None),

                              ) -> JSONResponse:

        valid, error_response, pat = self.auth_error_response(authorization)
        if not valid:
            return error_response

        can_write, error_response = self.repo_write_error_response(pat)
        if not can_write:
            return error_response

        if not self.state.repo_exists(owner, repo):
            return self.not_found_response()

        encrypted_value = body.get('encrypted_value')
        key_id          = body.get('key_id')

        # Validate required fields
        if not encrypted_value or not key_id:
            return JSONResponse(
                status_code=422,
                content={"message": "Invalid request. 'encrypted_value' and 'key_id' are required."}
            )

        existing = self.state.get_repo_secret(owner, repo, secret_name)

        self.state.set_repo_secret(owner, repo, secret_name, encrypted_value, key_id)

        if existing:
            return JSONResponse(content=None, status_code=204)
        else:
            return JSONResponse(content=None, status_code=201)

    @route_path('/repos/{owner}/{repo}/actions/secrets/{secret_name}')
    def delete_repo_secret(self, owner         : str              ,             # DELETE /repos/{owner}/{repo}/actions/secrets/{secret_name}
                                 repo          : str              ,
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

        deleted = self.state.delete_repo_secret(owner, repo, secret_name)
        if not deleted:
            return self.not_found_response()

        return JSONResponse(content=None, status_code=204)

    def setup_routes(self):                                                     # Register routes
        self.add_route_get   (self.get_repo_public_key)
        self.add_route_get   (self.list_repo_secrets  )
        self.add_route_get   (self.get_repo_secret    )
        self.add_route_put   (self.put_repo_secret    )
        self.add_route_delete(self.delete_repo_secret )
        return self
