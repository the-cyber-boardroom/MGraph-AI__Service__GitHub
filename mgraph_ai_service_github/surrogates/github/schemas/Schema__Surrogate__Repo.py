from typing                              import Optional, List
from osbot_utils.type_safe.Type_Safe     import Type_Safe


class Schema__Surrogate__Repo(Type_Safe):                                       # GitHub repository representation for surrogate
    owner        : str                                                          # Repository owner (user or org)
    name         : str                                                          # Repository name
    full_name    : str                                                          # Full name (owner/name)
    private      : bool                    = False                              # Is private repository
    environments : List[str]                                                    # List of environment names

    def repo_key(self) -> str:                                                  # Get unique key for this repo
        return self.full_name
