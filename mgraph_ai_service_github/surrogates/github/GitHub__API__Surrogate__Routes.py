from typing                                                                        import Dict, Any, Tuple, Optional
from fastapi                                                                       import FastAPI, Header, Request
from fastapi.responses                                                             import JSONResponse
from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__State      import GitHub__API__Surrogate__State
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__PATs       import GitHub__API__Surrogate__PATs
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__Keys       import GitHub__API__Surrogate__Keys


class GitHub__API__Surrogate__Routes(Type_Safe):                                # FastAPI route definitions for GitHub API surrogate
    
    state : GitHub__API__Surrogate__State
    pats  : GitHub__API__Surrogate__PATs
    keys  : GitHub__API__Surrogate__Keys
    
    def create_app(self) -> FastAPI:                                            # Create FastAPI app with all routes
        app = FastAPI(title="GitHub API Surrogate")
        
        # ═══════════════════════════════════════════════════════════════════════
        # Authentication helpers
        # ═══════════════════════════════════════════════════════════════════════
        
        def extract_pat(authorization: str) -> Optional[str]:                   # Extract PAT from Authorization header
            if not authorization:
                return None
            if authorization.startswith('token '):
                return authorization[6:]
            if authorization.startswith('Bearer '):
                return authorization[7:]
            return authorization
        
        def validate_auth(authorization: str) -> Tuple[bool, int, Dict[str, Any], str]:
            """Validate authorization and return (valid, status_code, error_response, pat)"""
            pat = extract_pat(authorization)
            
            if not pat:
                return (False, 401, self._error_response("Requires authentication", 401), None)
            
            if not self.pats.is_known_pat(pat):
                return (False, 401, self._error_response("Bad credentials", 401), None)
            
            if not self.pats.is_valid_pat(pat):
                return (False, 401, self._error_response("Bad credentials", 401), None)
            
            if self.pats.is_rate_limited(pat):
                return (False, 429, self._rate_limit_error(), None)
            
            return (True, 200, None, pat)
        
        def check_repo_read(pat: str) -> Tuple[bool, int, Dict[str, Any]]:
            """Check if PAT can read repo secrets"""
            if not self.pats.can_read_repo_secrets(pat):
                return (False, 403, self._error_response("Resource not accessible by integration", 403))
            return (True, 200, None)
        
        def check_repo_write(pat: str) -> Tuple[bool, int, Dict[str, Any]]:
            """Check if PAT can write repo secrets"""
            if not self.pats.can_write_repo_secrets(pat):
                return (False, 403, self._error_response("Resource not accessible by integration", 403))
            return (True, 200, None)
        
        def check_org_admin(pat: str) -> Tuple[bool, int, Dict[str, Any]]:
            """Check if PAT can admin org"""
            if not self.pats.can_admin_org(pat):
                return (False, 403, self._error_response("Resource not accessible by integration", 403))
            return (True, 200, None)
        
        # ═══════════════════════════════════════════════════════════════════════
        # Core endpoints
        # ═══════════════════════════════════════════════════════════════════════
        
        @app.get("/user")
        def get_user(authorization: str = Header(None)):                        # GET /user - Get authenticated user
            valid, status, error, pat = validate_auth(authorization)
            if not valid:
                return JSONResponse(content=error, status_code=status)
            
            user = self.pats.get_user(pat)
            if not user:
                return JSONResponse(content=self._error_response("Bad credentials", 401), status_code=401)
            
            return user.to_github_response()
        
        @app.get("/rate_limit")
        def get_rate_limit(authorization: str = Header(None)):                  # GET /rate_limit - Get rate limit status
            valid, status, error, pat = validate_auth(authorization)
            if not valid:
                return JSONResponse(content=error, status_code=status)
            
            rate_limit = self.state.get_rate_limit(pat)
            return rate_limit.to_github_response()
        
        # ═══════════════════════════════════════════════════════════════════════
        # Repository secrets endpoints
        # ═══════════════════════════════════════════════════════════════════════
        
        @app.get("/repos/{owner}/{repo}/actions/secrets/public-key")
        def get_repo_public_key(owner: str, repo: str,
                                authorization: str = Header(None)):
            valid, status, error, pat = validate_auth(authorization)
            if not valid:
                return JSONResponse(content=error, status_code=status)
            
            can_read, status, error = check_repo_read(pat)
            if not can_read:
                return JSONResponse(content=error, status_code=status)
            
            if not self.state.repo_exists(owner, repo):
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            public_key = self.keys.get_repo_public_key(owner, repo)
            self.state.set_public_key(self.keys.scope_id_for_repo(owner, repo), public_key)
            
            return public_key.to_github_response()
        
        @app.get("/repos/{owner}/{repo}/actions/secrets")
        def list_repo_secrets(owner: str, repo: str,
                              authorization: str = Header(None)):
            valid, status, error, pat = validate_auth(authorization)
            if not valid:
                return JSONResponse(content=error, status_code=status)
            
            can_read, status, error = check_repo_read(pat)
            if not can_read:
                return JSONResponse(content=error, status_code=status)
            
            if not self.state.repo_exists(owner, repo):
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            secrets      = self.state.list_repo_secrets(owner, repo)
            secrets_list = [s.to_github_response() for s in secrets]
            
            return dict(total_count = len(secrets_list) ,
                        secrets     = secrets_list      )
        
        @app.get("/repos/{owner}/{repo}/actions/secrets/{secret_name}")
        def get_repo_secret(owner: str, repo: str, secret_name: str,
                            authorization: str = Header(None)):
            valid, status, error, pat = validate_auth(authorization)
            if not valid:
                return JSONResponse(content=error, status_code=status)
            
            can_read, status, error = check_repo_read(pat)
            if not can_read:
                return JSONResponse(content=error, status_code=status)
            
            if not self.state.repo_exists(owner, repo):
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            secret = self.state.get_repo_secret(owner, repo, secret_name)
            if not secret:
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            return secret.to_github_response()
        
        @app.put("/repos/{owner}/{repo}/actions/secrets/{secret_name}")
        async def put_repo_secret(owner: str, repo: str, secret_name: str,
                                  request: Request,
                                  authorization: str = Header(None)):
            valid, status, error, pat = validate_auth(authorization)
            if not valid:
                return JSONResponse(content=error, status_code=status)
            
            can_write, status, error = check_repo_write(pat)
            if not can_write:
                return JSONResponse(content=error, status_code=status)
            
            if not self.state.repo_exists(owner, repo):
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            body            = await request.json()
            encrypted_value = body.get('encrypted_value', '')
            key_id          = body.get('key_id', '')
            
            # Check if secret already exists (for 201 vs 204)
            existing = self.state.get_repo_secret(owner, repo, secret_name)
            
            self.state.set_repo_secret(owner, repo, secret_name, encrypted_value, key_id)
            
            if existing:
                return JSONResponse(content=None, status_code=204)
            else:
                return JSONResponse(content=None, status_code=201)
        
        @app.delete("/repos/{owner}/{repo}/actions/secrets/{secret_name}")
        def delete_repo_secret(owner: str, repo: str, secret_name: str,
                               authorization: str = Header(None)):
            valid, status, error, pat = validate_auth(authorization)
            if not valid:
                return JSONResponse(content=error, status_code=status)
            
            can_write, status, error = check_repo_write(pat)
            if not can_write:
                return JSONResponse(content=error, status_code=status)
            
            if not self.state.repo_exists(owner, repo):
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            deleted = self.state.delete_repo_secret(owner, repo, secret_name)
            if not deleted:
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            return JSONResponse(content=None, status_code=204)
        
        # ═══════════════════════════════════════════════════════════════════════
        # Environment secrets endpoints
        # ═══════════════════════════════════════════════════════════════════════
        
        @app.get("/repos/{owner}/{repo}/environments/{environment}/secrets/public-key")
        def get_env_public_key(owner: str, repo: str, environment: str,
                               authorization: str = Header(None)):
            valid, status, error, pat = validate_auth(authorization)
            if not valid:
                return JSONResponse(content=error, status_code=status)
            
            can_read, status, error = check_repo_read(pat)
            if not can_read:
                return JSONResponse(content=error, status_code=status)
            
            if not self.state.repo_exists(owner, repo):
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            if not self.state.environment_exists(owner, repo, environment):
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            public_key = self.keys.get_env_public_key(owner, repo, environment)
            self.state.set_public_key(self.keys.scope_id_for_env(owner, repo, environment), public_key)
            
            return public_key.to_github_response()
        
        @app.get("/repos/{owner}/{repo}/environments/{environment}/secrets")
        def list_env_secrets(owner: str, repo: str, environment: str,
                             authorization: str = Header(None)):
            valid, status, error, pat = validate_auth(authorization)
            if not valid:
                return JSONResponse(content=error, status_code=status)
            
            can_read, status, error = check_repo_read(pat)
            if not can_read:
                return JSONResponse(content=error, status_code=status)
            
            if not self.state.repo_exists(owner, repo):
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            if not self.state.environment_exists(owner, repo, environment):
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            secrets      = self.state.list_env_secrets(owner, repo, environment)
            secrets_list = [s.to_github_response() for s in secrets]
            
            return dict(total_count = len(secrets_list) ,
                        secrets     = secrets_list      )
        
        @app.get("/repos/{owner}/{repo}/environments/{environment}/secrets/{secret_name}")
        def get_env_secret(owner: str, repo: str, environment: str, secret_name: str,
                           authorization: str = Header(None)):
            valid, status, error, pat = validate_auth(authorization)
            if not valid:
                return JSONResponse(content=error, status_code=status)
            
            can_read, status, error = check_repo_read(pat)
            if not can_read:
                return JSONResponse(content=error, status_code=status)
            
            if not self.state.repo_exists(owner, repo):
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            if not self.state.environment_exists(owner, repo, environment):
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            secret = self.state.get_env_secret(owner, repo, environment, secret_name)
            if not secret:
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            return secret.to_github_response()
        
        @app.put("/repos/{owner}/{repo}/environments/{environment}/secrets/{secret_name}")
        async def put_env_secret(owner: str, repo: str, environment: str, secret_name: str,
                                 request: Request,
                                 authorization: str = Header(None)):
            valid, status, error, pat = validate_auth(authorization)
            if not valid:
                return JSONResponse(content=error, status_code=status)
            
            can_write, status, error = check_repo_write(pat)
            if not can_write:
                return JSONResponse(content=error, status_code=status)
            
            if not self.state.repo_exists(owner, repo):
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            if not self.state.environment_exists(owner, repo, environment):
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            body            = await request.json()
            encrypted_value = body.get('encrypted_value', '')
            key_id          = body.get('key_id', '')
            
            existing = self.state.get_env_secret(owner, repo, environment, secret_name)
            
            self.state.set_env_secret(owner, repo, environment, secret_name, encrypted_value, key_id)
            
            if existing:
                return JSONResponse(content=None, status_code=204)
            else:
                return JSONResponse(content=None, status_code=201)
        
        @app.delete("/repos/{owner}/{repo}/environments/{environment}/secrets/{secret_name}")
        def delete_env_secret(owner: str, repo: str, environment: str, secret_name: str,
                              authorization: str = Header(None)):
            valid, status, error, pat = validate_auth(authorization)
            if not valid:
                return JSONResponse(content=error, status_code=status)
            
            can_write, status, error = check_repo_write(pat)
            if not can_write:
                return JSONResponse(content=error, status_code=status)
            
            if not self.state.repo_exists(owner, repo):
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            if not self.state.environment_exists(owner, repo, environment):
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            deleted = self.state.delete_env_secret(owner, repo, environment, secret_name)
            if not deleted:
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            return JSONResponse(content=None, status_code=204)
        
        # ═══════════════════════════════════════════════════════════════════════
        # Organization secrets endpoints
        # ═══════════════════════════════════════════════════════════════════════
        
        @app.get("/orgs/{org}/actions/secrets/public-key")
        def get_org_public_key(org: str,
                               authorization: str = Header(None)):
            valid, status, error, pat = validate_auth(authorization)
            if not valid:
                return JSONResponse(content=error, status_code=status)
            
            can_admin, status, error = check_org_admin(pat)
            if not can_admin:
                return JSONResponse(content=error, status_code=status)
            
            if not self.state.org_exists(org):
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            public_key = self.keys.get_org_public_key(org)
            self.state.set_public_key(self.keys.scope_id_for_org(org), public_key)
            
            return public_key.to_github_response()
        
        @app.get("/orgs/{org}/actions/secrets")
        def list_org_secrets(org: str,
                             authorization: str = Header(None)):
            valid, status, error, pat = validate_auth(authorization)
            if not valid:
                return JSONResponse(content=error, status_code=status)
            
            can_admin, status, error = check_org_admin(pat)
            if not can_admin:
                return JSONResponse(content=error, status_code=status)
            
            if not self.state.org_exists(org):
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            secrets      = self.state.list_org_secrets(org)
            secrets_list = [s.to_github_response() for s in secrets]
            
            return dict(total_count = len(secrets_list) ,
                        secrets     = secrets_list      )
        
        @app.get("/orgs/{org}/actions/secrets/{secret_name}")
        def get_org_secret(org: str, secret_name: str,
                           authorization: str = Header(None)):
            valid, status, error, pat = validate_auth(authorization)
            if not valid:
                return JSONResponse(content=error, status_code=status)
            
            can_admin, status, error = check_org_admin(pat)
            if not can_admin:
                return JSONResponse(content=error, status_code=status)
            
            if not self.state.org_exists(org):
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            secret = self.state.get_org_secret(org, secret_name)
            if not secret:
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            return secret.to_github_response()
        
        @app.put("/orgs/{org}/actions/secrets/{secret_name}")
        async def put_org_secret(org: str, secret_name: str,
                                 request: Request,
                                 authorization: str = Header(None)):
            valid, status, error, pat = validate_auth(authorization)
            if not valid:
                return JSONResponse(content=error, status_code=status)
            
            can_admin, status, error = check_org_admin(pat)
            if not can_admin:
                return JSONResponse(content=error, status_code=status)
            
            if not self.state.org_exists(org):
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
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
        
        @app.delete("/orgs/{org}/actions/secrets/{secret_name}")
        def delete_org_secret(org: str, secret_name: str,
                              authorization: str = Header(None)):
            valid, status, error, pat = validate_auth(authorization)
            if not valid:
                return JSONResponse(content=error, status_code=status)
            
            can_admin, status, error = check_org_admin(pat)
            if not can_admin:
                return JSONResponse(content=error, status_code=status)
            
            if not self.state.org_exists(org):
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            deleted = self.state.delete_org_secret(org, secret_name)
            if not deleted:
                return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
            
            return JSONResponse(content=None, status_code=204)
        
        return app
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # Error response helpers
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def _error_response(self, message: str, status_code: int) -> Dict[str, Any]:
        return dict(message           = message                        ,
                    documentation_url = 'https://docs.github.com/rest' )
    
    def _rate_limit_error(self) -> Dict[str, Any]:
        return dict(message           = 'API rate limit exceeded for user'        ,
                    documentation_url = 'https://docs.github.com/rest/rate-limit' )
