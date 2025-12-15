from mgraph_ai_service_github.schemas.base.Schema__Response__Data import Schema__Response__Data


class Schema__GitHub__Data__Secret__Delete(Schema__Response__Data):             # Response data for deleting a secret
    deleted: bool = False                                                       # Whether the secret was deleted successfully
