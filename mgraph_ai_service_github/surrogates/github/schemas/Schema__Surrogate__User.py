from typing                              import Optional, Dict, Any
from osbot_utils.type_safe.Type_Safe     import Type_Safe


class Schema__Surrogate__User(Type_Safe):                                       # GitHub user representation for surrogate
    login                     : str
    id                        : int
    name                      : Optional[str]           = None
    email                     : Optional[str]           = None
    company                   : Optional[str]           = None
    created_at                : Optional[str]           = None
    public_repos              : int                     = 0
    total_private_repos       : int                     = 0
    owned_private_repos       : int                     = 0
    collaborators             : int                     = 0
    two_factor_authentication : bool                    = False
    plan                      : Optional[Dict[str, Any]] = None

    def to_github_response(self) -> Dict[str, Any]:                             # Convert to GitHub API response format
        response = dict(login                     = self.login                     ,
                        id                        = self.id                        ,
                        name                      = self.name                      ,
                        email                     = self.email                     ,
                        company                   = self.company                   ,
                        created_at                = self.created_at                ,
                        public_repos              = self.public_repos              ,
                        total_private_repos       = self.total_private_repos       ,
                        owned_private_repos       = self.owned_private_repos       ,
                        collaborators             = self.collaborators             ,
                        two_factor_authentication = self.two_factor_authentication )
        if self.plan:
            response['plan'] = self.plan
        return response
