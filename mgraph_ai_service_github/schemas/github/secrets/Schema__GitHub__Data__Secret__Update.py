from mgraph_ai_service_github.schemas.base.Schema__Response__Data import Schema__Response__Data


class Schema__GitHub__Data__Secret__Update(Schema__Response__Data):             # Response data for updating a secret
    updated: bool = False                                                       # Whether the secret was updated successfully
