from mgraph_ai_service_github.schemas.base.Schema__Response__Data import Schema__Response__Data


class Schema__GitHub__Data__Secret__Create(Schema__Response__Data):             # Response data for creating a secret
    created: bool = False                                                       # Whether the secret was created successfully
