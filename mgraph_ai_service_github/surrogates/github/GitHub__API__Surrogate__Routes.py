from fastapi                                                                               import FastAPI
from osbot_utils.type_safe.Type_Safe                                                       import Type_Safe
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__State              import GitHub__API__Surrogate__State
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__PATs               import GitHub__API__Surrogate__PATs
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__Keys               import GitHub__API__Surrogate__Keys
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__Fast_API           import GitHub__API__Surrogate__Fast_API


class GitHub__API__Surrogate__Routes(Type_Safe):                                # FastAPI route definitions for GitHub API surrogate
    
    state : GitHub__API__Surrogate__State
    pats  : GitHub__API__Surrogate__PATs
    keys  : GitHub__API__Surrogate__Keys

    def create_app(self) -> FastAPI:                                            # Create FastAPI app with all routes
        with GitHub__API__Surrogate__Fast_API() as fast_api:
            fast_api.state = self.state
            fast_api.pats  = self.pats
            fast_api.keys  = self.keys
            fast_api.setup()
            return fast_api.app()
