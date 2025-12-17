from typing                                                                        import Dict, Any, Tuple, Optional
from fastapi.responses                                                             import JSONResponse
from osbot_fast_api.api.routes.Fast_API__Routes                                    import Fast_API__Routes


class Routes__GitHub__Base(Fast_API__Routes):                                   # Base class for GitHub surrogate routes with shared auth helpers
    tag   : str = None                                                          # Subclasses should not set tag (GitHub API has no prefix)
    state : object = None                                                       # GitHub__API__Surrogate__State - injected
    pats  : object = None                                                       # GitHub__API__Surrogate__PATs - injected
    keys  : object = None                                                       # GitHub__API__Surrogate__Keys - injected

    # ═══════════════════════════════════════════════════════════════════════════════
    # Authentication helpers
    # ═══════════════════════════════════════════════════════════════════════════════

    def extract_pat(self, authorization: str) -> Optional[str]:                 # Extract PAT from Authorization header
        if not authorization:
            return None
        if authorization.startswith('token '):
            return authorization[6:]
        if authorization.startswith('Bearer '):
            return authorization[7:]
        return authorization

    def validate_auth(self, authorization: str                                  # Validate authorization and return (valid, status_code, error_response, pat)
                      ) -> Tuple[bool, int, Dict[str, Any], str]:
        pat = self.extract_pat(authorization)

        if not pat:
            return (False, 401, self._error_response("Requires authentication", 401), None)

        if not self.pats.is_known_pat(pat):
            return (False, 401, self._error_response("Bad credentials", 401), None)

        if not self.pats.is_valid_pat(pat):
            return (False, 401, self._error_response("Bad credentials", 401), None)

        if self.pats.is_rate_limited(pat):
            return (False, 429, self._rate_limit_error(), None)

        return (True, 200, None, pat)

    def check_repo_read(self, pat: str                                          # Check if PAT can read repo secrets
                        ) -> Tuple[bool, int, Dict[str, Any]]:
        if not self.pats.can_read_repo_secrets(pat):
            return (False, 403, self._error_response("Resource not accessible by integration", 403))
        return (True, 200, None)

    def check_repo_write(self, pat: str                                         # Check if PAT can write repo secrets
                         ) -> Tuple[bool, int, Dict[str, Any]]:
        if not self.pats.can_write_repo_secrets(pat):
            return (False, 403, self._error_response("Resource not accessible by integration", 403))
        return (True, 200, None)

    def check_org_admin(self, pat: str                                          # Check if PAT can admin org
                        ) -> Tuple[bool, int, Dict[str, Any]]:
        if not self.pats.can_admin_org(pat):
            return (False, 403, self._error_response("Resource not accessible by integration", 403))
        return (True, 200, None)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Error response helpers
    # ═══════════════════════════════════════════════════════════════════════════════

    def _error_response(self, message: str, status_code: int) -> Dict[str, Any]:
        return dict(message           = message                        ,
                    documentation_url = 'https://docs.github.com/rest' )

    def _rate_limit_error(self) -> Dict[str, Any]:
        return dict(message           = 'API rate limit exceeded for user'        ,
                    documentation_url = 'https://docs.github.com/rest/rate-limit' )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Response helpers for auth failures
    # ═══════════════════════════════════════════════════════════════════════════════

    def auth_error_response(self, authorization: str                            # Validate auth and return error response if invalid
                            ) -> Tuple[bool, Optional[JSONResponse], Optional[str]]:
        valid, status, error, pat = self.validate_auth(authorization)
        if not valid:
            return (False, JSONResponse(content=error, status_code=status), None)
        return (True, None, pat)

    def repo_read_error_response(self, pat: str                                 # Check repo read permission and return error response if denied
                                 ) -> Tuple[bool, Optional[JSONResponse]]:
        can_read, status, error = self.check_repo_read(pat)
        if not can_read:
            return (False, JSONResponse(content=error, status_code=status))
        return (True, None)

    def repo_write_error_response(self, pat: str                                # Check repo write permission and return error response if denied
                                  ) -> Tuple[bool, Optional[JSONResponse]]:
        can_write, status, error = self.check_repo_write(pat)
        if not can_write:
            return (False, JSONResponse(content=error, status_code=status))
        return (True, None)

    def org_admin_error_response(self, pat: str                                 # Check org admin permission and return error response if denied
                                 ) -> Tuple[bool, Optional[JSONResponse]]:
        can_admin, status, error = self.check_org_admin(pat)
        if not can_admin:
            return (False, JSONResponse(content=error, status_code=status))
        return (True, None)

    def not_found_response(self) -> JSONResponse:                               # Return 404 Not Found response
        return JSONResponse(content=self._error_response("Not Found", 404), status_code=404)
