from enum import Enum


class Enum__GitHub__Scope(Enum):                                                # GitHub OAuth scopes for PAT permissions
    REPO                = 'repo'                                                # Full control of private repositories
    PUBLIC_REPO         = 'public_repo'                                         # Access public repositories only
    ADMIN_ORG           = 'admin:org'                                           # Full organization admin access
    WRITE_ORG           = 'write:org'                                           # Read/write organization membership
    READ_ORG            = 'read:org'                                            # Read organization membership
    WORKFLOW            = 'workflow'                                            # Update GitHub Actions workflows
