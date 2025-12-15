from typing                                                                              import List
from fastapi                                                                             import Response
from osbot_utils.helpers.duration.decorators.capture_duration                            import capture_duration
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text             import Safe_Str__Text
from osbot_fast_api.api.routes.Fast_API__Routes                                          import Fast_API__Routes
from mgraph_ai_service_github.fast_api.dependencies.GitHub__API__From__Header            import GitHub__API__From__Header
from mgraph_ai_service_github.schemas.base.Enum__HTTP__Status                            import Enum__HTTP__Status
from mgraph_ai_service_github.schemas.base.Enum__Error__Type                             import Enum__Error__Type
from mgraph_ai_service_github.schemas.github.base.Schema__GitHub__Rate_Limit             import Schema__GitHub__Rate_Limit
from mgraph_ai_service_github.schemas.github.base.Schema__GitHub__Response__Context      import Schema__GitHub__Response__Context
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Org__Secret__Metadata import Schema__GitHub__Org__Secret__Metadata
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Org__Secrets__List import Schema__GitHub__Data__Org__Secrets__List
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Org__Secret__Operations import (
    Schema__GitHub__Data__Org__Secret__Get    ,
    Schema__GitHub__Data__Org__Secret__Create ,
    Schema__GitHub__Data__Org__Secret__Update ,
    Schema__GitHub__Data__Org__Secret__Delete )
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Request__Org__Secrets__List import Schema__GitHub__Request__Org__Secrets__List
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Response__Org__Secrets__List import Schema__GitHub__Response__Org__Secrets__List
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Request__Org__Secret__Operations import (
    Schema__GitHub__Request__Org__Secret__Get    ,
    Schema__GitHub__Request__Org__Secret__Create ,
    Schema__GitHub__Request__Org__Secret__Update ,
    Schema__GitHub__Request__Org__Secret__Delete )
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Response__Org__Secret__Operations import (
    Schema__GitHub__Response__Org__Secret__Get    ,
    Schema__GitHub__Response__Org__Secret__Create ,
    Schema__GitHub__Response__Org__Secret__Update ,
    Schema__GitHub__Response__Org__Secret__Delete )
from mgraph_ai_service_github.service.github.GitHub__Secrets                             import GitHub__Secrets
from mgraph_ai_service_github.service.encryption.Service__Encryption                     import Service__Encryption

TAG__ROUTES_GITHUB_SECRETS_ORG   = 'github-secrets-org'
ROUTES_PATHS__GITHUB_SECRETS_ORG = [ f'/{TAG__ROUTES_GITHUB_SECRETS_ORG}/list'   ,
                                     f'/{TAG__ROUTES_GITHUB_SECRETS_ORG}/get'    ,
                                     f'/{TAG__ROUTES_GITHUB_SECRETS_ORG}/create' ,
                                     f'/{TAG__ROUTES_GITHUB_SECRETS_ORG}/update' ,
                                     f'/{TAG__ROUTES_GITHUB_SECRETS_ORG}/delete' ]

# todo: refactor these classes so that we don't have any logic here (just FastAPI response handling code)

class Routes__GitHub__Secrets__Org(Fast_API__Routes):                           # Routes for managing organization secrets
    tag               : str                       = TAG__ROUTES_GITHUB_SECRETS_ORG
    github_api_factory: GitHub__API__From__Header
    service_encryption: Service__Encryption

    def list(self, request : Schema__GitHub__Request__Org__Secrets__List ,      # List all secrets in an organization
                   response: Response
             ) -> Schema__GitHub__Response__Org__Secrets__List:

        with capture_duration() as duration:
            response_context = Schema__GitHub__Response__Context()
            response_data    = Schema__GitHub__Data__Org__Secrets__List()

            try:
                github_api     = self.github_api_factory.get_api(request.encrypted_pat)
                request_data   = request.request_data
                github_secrets = GitHub__Secrets(api_token = github_api.api_token    ,
                                                 repo_name = "placeholder/placeholder")  # Org secrets don't need repo

                secrets_list = github_secrets.list_org_secrets(str(request_data.org))

                for secret in secrets_list:
                    metadata = Schema__GitHub__Org__Secret__Metadata(
                        name                      = secret.get('name'                     ) ,
                        created_at                = secret.get('created_at'               ) ,
                        updated_at                = secret.get('updated_at'               ) ,
                        visibility                = secret.get('visibility'               ) ,
                        selected_repositories_url = secret.get('selected_repositories_url') )
                    response_data.secrets.append(metadata)

                self._populate_rate_limit(github_api, response_context)

                response_context.success     = True
                response_context.status_code = Enum__HTTP__Status.OK_200

            except ValueError as e:
                response_context.status_code = Enum__HTTP__Status.UNAUTHORIZED_401
                response_context.error_type  = Enum__Error__Type.DECRYPTION_FAILED
                response_context.errors.append(Safe_Str__Text(str(e)))

            except Exception as e:
                self._handle_github_error(e, response_context)

        response_context.duration = duration.seconds

        response.status_code = response_context.status_code.value
        return Schema__GitHub__Response__Org__Secrets__List(response_context = response_context ,
                                                            response_data    = response_data    )

    def get(self, request : Schema__GitHub__Request__Org__Secret__Get ,         # Get metadata for a single org secret
                  response: Response
            ) -> Schema__GitHub__Response__Org__Secret__Get:

        with capture_duration() as duration:
            response_context = Schema__GitHub__Response__Context()
            response_data    = Schema__GitHub__Data__Org__Secret__Get()

            try:
                github_api     = self.github_api_factory.get_api(request.encrypted_pat)
                request_data   = request.request_data
                org_name       = str(request_data.org)
                secret_name    = str(request_data.secret_name)
                github_secrets = GitHub__Secrets(api_token = github_api.api_token     ,
                                                 repo_name = "placeholder/placeholder")

                secret = github_secrets.get_org_secret(org_name, secret_name)

                if secret:
                    response_data.secret = Schema__GitHub__Org__Secret__Metadata(
                        name                      = secret.get('name'                     ) ,
                        created_at                = secret.get('created_at'               ) ,
                        updated_at                = secret.get('updated_at'               ) ,
                        visibility                = secret.get('visibility'               ) ,
                        selected_repositories_url = secret.get('selected_repositories_url') )
                    response_context.success     = True
                    response_context.status_code = Enum__HTTP__Status.OK_200
                else:
                    response_context.status_code = Enum__HTTP__Status.NOT_FOUND_404
                    response_context.error_type  = Enum__Error__Type.NOT_FOUND

                self._populate_rate_limit(github_api, response_context)

            except ValueError as e:
                response_context.status_code = Enum__HTTP__Status.UNAUTHORIZED_401
                response_context.error_type  = Enum__Error__Type.DECRYPTION_FAILED
                response_context.errors.append(Safe_Str__Text(str(e)))

            except Exception as e:
                self._handle_github_error(e, response_context)

            finally:
                response_context.duration = duration.seconds

        response.status_code = response_context.status_code.value
        return Schema__GitHub__Response__Org__Secret__Get(response_context = response_context ,
                                                          response_data    = response_data    )

    def create(self, request : Schema__GitHub__Request__Org__Secret__Create ,   # Create a new organization secret
                     response: Response
               ) -> Schema__GitHub__Response__Org__Secret__Create:

        with capture_duration() as duration:
            response_context = Schema__GitHub__Response__Context()
            response_data    = Schema__GitHub__Data__Org__Secret__Create()

            try:
                github_api     = self.github_api_factory.get_api(request.encrypted_pat)
                request_data   = request.request_data
                github_secrets = GitHub__Secrets(api_token = github_api.api_token    ,
                                                 repo_name = "placeholder/placeholder")

                decrypted_value = self._decrypt_secret_value(request_data.encrypted_value)

                created = github_secrets.create_or_update_org_secret(
                    org_name     = str(request_data.org)         ,
                    secret_name  = str(request_data.secret_name) ,
                    secret_value = decrypted_value               ,
                    visibility   = request_data.visibility       ,
                    repo_ids     = request_data.repo_ids         )

                response_data.created = created

                if created:
                    response_context.success     = True
                    response_context.status_code = Enum__HTTP__Status.CREATED_201
                    response_context.messages.append(Safe_Str__Text(f"Org secret '{request_data.secret_name}' created"))
                else:
                    response_context.status_code = Enum__HTTP__Status.SERVER_ERROR_500
                    response_context.error_type  = Enum__Error__Type.GITHUB_API_ERROR
                    response_context.errors.append(Safe_Str__Text("Failed to create org secret"))

                self._populate_rate_limit(github_api, response_context)

            except ValueError as e:
                response_context.status_code = Enum__HTTP__Status.UNAUTHORIZED_401
                response_context.error_type  = Enum__Error__Type.DECRYPTION_FAILED
                response_context.errors.append(Safe_Str__Text(str(e)))

            except Exception as e:
                self._handle_github_error(e, response_context)

            finally:
                response_context.duration = duration.seconds

        response.status_code = response_context.status_code.value
        return Schema__GitHub__Response__Org__Secret__Create(response_context = response_context ,
                                                             response_data    = response_data    )

    def update(self, request : Schema__GitHub__Request__Org__Secret__Update ,   # Update an existing organization secret
                     response: Response
               ) -> Schema__GitHub__Response__Org__Secret__Update:

        with capture_duration() as duration:
            response_context = Schema__GitHub__Response__Context()
            response_data    = Schema__GitHub__Data__Org__Secret__Update()

            try:
                github_api     = self.github_api_factory.get_api(request.encrypted_pat)
                request_data   = request.request_data
                github_secrets = GitHub__Secrets(api_token = github_api.api_token    ,
                                                 repo_name = "placeholder/placeholder")

                decrypted_value = self._decrypt_secret_value(request_data.encrypted_value)

                updated = github_secrets.create_or_update_org_secret(
                    org_name     = str(request_data.org)         ,
                    secret_name  = str(request_data.secret_name) ,
                    secret_value = decrypted_value               ,
                    visibility   = request_data.visibility       ,
                    repo_ids     = request_data.repo_ids         )

                response_data.updated = updated

                if updated:
                    response_context.success     = True
                    response_context.status_code = Enum__HTTP__Status.OK_200
                    response_context.messages.append(Safe_Str__Text(f"Org secret '{request_data.secret_name}' updated"))
                else:
                    response_context.status_code = Enum__HTTP__Status.SERVER_ERROR_500
                    response_context.error_type  = Enum__Error__Type.GITHUB_API_ERROR
                    response_context.errors.append(Safe_Str__Text("Failed to update org secret"))

                self._populate_rate_limit(github_api, response_context)

            except ValueError as e:
                response_context.status_code = Enum__HTTP__Status.UNAUTHORIZED_401
                response_context.error_type  = Enum__Error__Type.DECRYPTION_FAILED
                response_context.errors.append(Safe_Str__Text(str(e)))

            except Exception as e:
                self._handle_github_error(e, response_context)

            finally:
                response_context.duration = duration.seconds

        response.status_code = response_context.status_code.value
        return Schema__GitHub__Response__Org__Secret__Update(response_context = response_context ,
                                                             response_data    = response_data    )

    def delete(self, request : Schema__GitHub__Request__Org__Secret__Delete ,   # Delete an organization secret
                     response: Response
               ) -> Schema__GitHub__Response__Org__Secret__Delete:

        with capture_duration() as duration:
            response_context = Schema__GitHub__Response__Context()
            response_data    = Schema__GitHub__Data__Org__Secret__Delete()

            try:
                github_api     = self.github_api_factory.get_api(request.encrypted_pat)
                request_data   = request.request_data
                org_name       = str(request_data.org)
                secret_name    = str(request_data.secret_name)
                github_secrets = GitHub__Secrets(api_token = github_api.api_token     ,
                                                 repo_name = "placeholder/placeholder")

                deleted = github_secrets.delete_org_secret(org_name, secret_name)

                response_data.deleted = deleted

                if deleted:
                    response_context.success     = True
                    response_context.status_code = Enum__HTTP__Status.OK_200
                    response_context.messages.append(Safe_Str__Text(f"Org secret '{secret_name}' deleted"))
                else:
                    response_context.status_code = Enum__HTTP__Status.NOT_FOUND_404
                    response_context.error_type  = Enum__Error__Type.NOT_FOUND
                    response_context.errors.append(Safe_Str__Text(f"Org secret '{secret_name}' not found"))

                self._populate_rate_limit(github_api, response_context)

            except ValueError as e:
                response_context.status_code = Enum__HTTP__Status.UNAUTHORIZED_401
                response_context.error_type  = Enum__Error__Type.DECRYPTION_FAILED
                response_context.errors.append(Safe_Str__Text(str(e)))

            except Exception as e:
                self._handle_github_error(e, response_context)

            finally:
                response_context.duration = duration.seconds

        response.status_code = response_context.status_code.value
        return Schema__GitHub__Response__Org__Secret__Delete(response_context = response_context ,
                                                             response_data    = response_data    )

    def setup_routes(self):
        self.add_route_post  (self.list  )
        self.add_route_post  (self.get   )
        self.add_route_post  (self.create)
        self.add_route_put   (self.update)
        self.add_route_delete(self.delete)

    def _decrypt_secret_value(self, encrypted_value: str) -> str:
        result = self.service_encryption.decrypt_text(encrypted_value)
        if not result.success:
            raise ValueError("Failed to decrypt secret value")
        return str(result.decrypted)

    def _populate_rate_limit(self, github_api, response_context: Schema__GitHub__Response__Context) -> None:
        try:
            rate_limit_data = github_api.get('/rate_limit')
            rate_info       = rate_limit_data.get('rate', {})
            response_context.rate_limit = Schema__GitHub__Rate_Limit(limit     = rate_info.get('limit'    ) ,
                                                                     remaining = rate_info.get('remaining') ,
                                                                     reset     = rate_info.get('reset'    ) ,
                                                                     used      = rate_info.get('used'     ) )
        except Exception:
            pass

    def _handle_github_error(self, error, response_context: Schema__GitHub__Response__Context) -> None:
        error_str = str(error)
        if "401" in error_str:
            response_context.status_code = Enum__HTTP__Status.UNAUTHORIZED_401
            response_context.error_type  = Enum__Error__Type.INVALID_PAT
        elif "403" in error_str and "rate limit" in error_str.lower():
            response_context.status_code = Enum__HTTP__Status.RATE_LIMITED_429
            response_context.error_type  = Enum__Error__Type.RATE_LIMITED
        elif "403" in error_str:
            response_context.status_code = Enum__HTTP__Status.FORBIDDEN_403
            response_context.error_type  = Enum__Error__Type.FORBIDDEN
        elif "404" in error_str:
            response_context.status_code = Enum__HTTP__Status.NOT_FOUND_404
            response_context.error_type  = Enum__Error__Type.NOT_FOUND
        else:
            response_context.status_code = Enum__HTTP__Status.SERVER_ERROR_500
            response_context.error_type  = Enum__Error__Type.GITHUB_API_ERROR
        response_context.errors.append(Safe_Str__Text(f"GitHub API error: {error_str}"))
