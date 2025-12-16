from unittest                                                                       import TestCase
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate              import GitHub__API__Surrogate

class test__GitHub__API__Surrogate__Routes(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.surrogate = (GitHub__API__Surrogate()    
                            .setup()
                            .add_repo       ("test-org", "test-repo")
                            .add_environment("test-org", "test-repo", "production")
                            .add_secret     ("test-org", "test-repo", "EXISTING_SECRET")
                            .add_env_secret ("test-org", "test-repo", "production", "ENV_SECRET")
                            .add_org        ("test-org")
                            .add_org_secret ("test-org", "ORG_SECRET"))
    
        cls.client = cls.surrogate.test_client()

    def test_get_user(self):
        pats = self.surrogate.pats
        # Valid auth
        response = self.client.get("/user", headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 200
        data = response.json()
        assert data["login"] == "surrogate-admin"

        # No auth
        response = self.client.get("/user")
        assert response.status_code == 401

        # Invalid auth
        response = self.client.get("/user", headers={"Authorization": "token invalid"})
        assert response.status_code == 401

        # Expired token
        response = self.client.get("/user", headers={"Authorization": f"token {pats.expired_pat()}"})
        assert response.status_code == 401

        # Rate limited
        response = self.client.get("/user", headers={"Authorization": f"token {pats.rate_limited_pat()}"})
        assert response.status_code == 429

    def test_get_rate_limit(self):
        pats     = self.surrogate.pats
        response = self.client.get("/rate_limit", headers={"Authorization": f"token {pats.admin_pat()}"})

        assert response.status_code == 200
        data = response.json()
        assert "rate" in data
        assert data["rate"]["limit"] == 5000

    def test_repo_secrets_public_key(self):
        pats     = self.surrogate.pats
        response = self.client.get("/repos/test-org/test-repo/actions/secrets/public-key",
                                     headers={"Authorization": f"token {pats.admin_pat()}"})

        assert response.status_code == 200
        data = response.json()
        assert "key_id" in data
        assert "key"    in data

    def test_list_repo_secrets(self):
        pats     = self.surrogate.pats
        response = self.client.get("/repos/test-org/test-repo/actions/secrets",
                                     headers={"Authorization": f"token {pats.admin_pat()}"})

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 2
        assert len(data["secrets"]) == 2
        assert data["secrets"][0]["name"] == "EXISTING_SECRET"

    def test_get_repo_secret(self):
        pats = self.surrogate.pats

        # Existing secret
        response = self.client.get("/repos/test-org/test-repo/actions/secrets/EXISTING_SECRET",
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "EXISTING_SECRET"

        # Non-existent secret
        response = self.client.get("/repos/test-org/test-repo/actions/secrets/NONEXISTENT",
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 404

    def test_create_repo_secret(self):
        pats = self.surrogate.pats

        # Get public key first
        key_response = self.client.get("/repos/test-org/test-repo/actions/secrets/public-key",
                                         headers={"Authorization": f"token {pats.admin_pat()}"})
        key_data = key_response.json()

        # Create new secret
        encrypted_value = self.surrogate.encrypt_for_repo("test-org", "test-repo", "new_value")
        response = self.client.put("/repos/test-org/test-repo/actions/secrets/NEW_SECRET",
                                     json={"encrypted_value": encrypted_value, "key_id": key_data["key_id"]},
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 201

        # Verify it exists
        response = self.client.get("/repos/test-org/test-repo/actions/secrets/NEW_SECRET",
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 200

        # Update existing (should be 204)
        response = self.client.put("/repos/test-org/test-repo/actions/secrets/NEW_SECRET",
                                     json={"encrypted_value": encrypted_value, "key_id": key_data["key_id"]},
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 204

    def test_delete_repo_secret(self):
        pats = self.surrogate.pats

        # Add a secret to delete (since state is shared and another test might have deleted it)
        self.surrogate.add_secret("test-org", "test-repo", "SECRET_TO_DELETE")

        # Delete existing
        response = self.client.delete("/repos/test-org/test-repo/actions/secrets/SECRET_TO_DELETE",
                                        headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 204

        # Delete non-existent
        response = self.client.delete("/repos/test-org/test-repo/actions/secrets/NONEXISTENT",
                                        headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 404

    def test_permission_denied_repo_read(self):
        pats = self.surrogate.pats

        # No scopes PAT cannot read
        response = self.client.get("/repos/test-org/test-repo/actions/secrets",
                                     headers={"Authorization": f"token {pats.no_scopes_pat()}"})
        assert response.status_code == 403

    def test_permission_denied_repo_write(self):
        pats = self.surrogate.pats

        # Read-only PAT cannot write
        response = self.client.put("/repos/test-org/test-repo/actions/secrets/TEST",
                                     json={"encrypted_value": "test", "key_id": "123"},
                                     headers={"Authorization": f"token {pats.repo_read_pat()}"})
        assert response.status_code == 403

    def test_repo_not_found(self):
        pats     = self.surrogate.pats
        response = self.client.get("/repos/nonexistent/repo/actions/secrets",
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 404

    def test_env_secrets(self):
        pats = self.surrogate.pats

        # List env secrets
        response = self.client.get("/repos/test-org/test-repo/environments/production/secrets",
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 2

        # Get env secret
        response = self.client.get("/repos/test-org/test-repo/environments/production/secrets/ENV_SECRET",
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 200

        # Non-existent environment
        response = self.client.get("/repos/test-org/test-repo/environments/staging/secrets",
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 404

    def test_org_secrets(self):
        pats = self.surrogate.pats

        # List org secrets (requires org admin)
        response = self.client.get("/orgs/test-org/actions/secrets",
                                     headers={"Authorization": f"token {pats.org_admin_pat()}"})
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 2

        # Get org secret
        response = self.client.get("/orgs/test-org/actions/secrets/ORG_SECRET",
                                     headers={"Authorization": f"token {pats.org_admin_pat()}"})
        assert response.status_code == 200

        # Repo-only PAT cannot access org secrets
        response = self.client.get("/orgs/test-org/actions/secrets",
                                     headers={"Authorization": f"token {pats.repo_write_pat()}"})
        assert response.status_code == 403

    def test_create_env_secret(self):
        pats = self.surrogate.pats

        # Get public key first
        key_response = self.client.get("/repos/test-org/test-repo/environments/production/secrets/public-key",
                                         headers={"Authorization": f"token {pats.admin_pat()}"})
        assert key_response.status_code == 200
        key_data = key_response.json()

        # Create new env secret
        encrypted_value = self.surrogate.encrypt_for_env("test-org", "test-repo", "production", "new_value")
        response = self.client.put("/repos/test-org/test-repo/environments/production/secrets/NEW_ENV_SECRET",
                                     json={"encrypted_value": encrypted_value, "key_id": key_data["key_id"]},
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 201

        # Update existing (should be 204)
        response = self.client.put("/repos/test-org/test-repo/environments/production/secrets/NEW_ENV_SECRET",
                                     json={"encrypted_value": encrypted_value, "key_id": key_data["key_id"]},
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 204

    def test_delete_env_secret(self):
        pats = self.surrogate.pats

        # Add a secret to delete
        self.surrogate.add_env_secret("test-org", "test-repo", "production", "ENV_TO_DELETE")

        # Delete existing
        response = self.client.delete("/repos/test-org/test-repo/environments/production/secrets/ENV_TO_DELETE",
                                        headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 204

        # Delete non-existent
        response = self.client.delete("/repos/test-org/test-repo/environments/production/secrets/NONEXISTENT",
                                        headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 404

    def test_env_secret_permission_denied(self):
        pats = self.surrogate.pats

        # Read-only PAT cannot write env secrets
        response = self.client.put("/repos/test-org/test-repo/environments/production/secrets/TEST",
                                     json={"encrypted_value": "test", "key_id": "123"},
                                     headers={"Authorization": f"token {pats.repo_read_pat()}"})
        assert response.status_code == 403

        # Read-only PAT cannot delete env secrets
        response = self.client.delete("/repos/test-org/test-repo/environments/production/secrets/ENV_SECRET",
                                        headers={"Authorization": f"token {pats.repo_read_pat()}"})
        assert response.status_code == 403

    def test_org_public_key(self):
        pats     = self.surrogate.pats
        response = self.client.get("/orgs/test-org/actions/secrets/public-key",
                                     headers={"Authorization": f"token {pats.org_admin_pat()}"})

        assert response.status_code == 200
        data = response.json()
        assert "key_id" in data
        assert "key"    in data

    def test_create_org_secret(self):
        pats = self.surrogate.pats

        # Get public key first
        key_response = self.client.get("/orgs/test-org/actions/secrets/public-key",
                                         headers={"Authorization": f"token {pats.org_admin_pat()}"})
        key_data = key_response.json()

        # Create new org secret
        encrypted_value = self.surrogate.encrypt_for_org("test-org", "new_value")
        response = self.client.put("/orgs/test-org/actions/secrets/NEW_ORG_SECRET",
                                     json={"encrypted_value": encrypted_value, "key_id": key_data["key_id"], "visibility": "private"},
                                     headers={"Authorization": f"token {pats.org_admin_pat()}"})
        assert response.status_code == 201

        # Update existing (should be 204)
        response = self.client.put("/orgs/test-org/actions/secrets/NEW_ORG_SECRET",
                                     json={"encrypted_value": encrypted_value, "key_id": key_data["key_id"], "visibility": "all"},
                                     headers={"Authorization": f"token {pats.org_admin_pat()}"})
        assert response.status_code == 204

    def test_delete_org_secret(self):
        pats = self.surrogate.pats

        # Add a secret to delete
        self.surrogate.add_org_secret("test-org", "ORG_TO_DELETE")

        # Delete existing
        response = self.client.delete("/orgs/test-org/actions/secrets/ORG_TO_DELETE",
                                        headers={"Authorization": f"token {pats.org_admin_pat()}"})
        assert response.status_code == 204

        # Delete non-existent
        response = self.client.delete("/orgs/test-org/actions/secrets/NONEXISTENT",
                                        headers={"Authorization": f"token {pats.org_admin_pat()}"})
        assert response.status_code == 404

    def test_org_not_found(self):
        pats = self.surrogate.pats

        response = self.client.get("/orgs/nonexistent-org/actions/secrets",
                                     headers={"Authorization": f"token {pats.org_admin_pat()}"})
        assert response.status_code == 404

        response = self.client.get("/orgs/nonexistent-org/actions/secrets/public-key",
                                     headers={"Authorization": f"token {pats.org_admin_pat()}"})
        assert response.status_code == 404

    def test_org_permission_denied(self):
        pats = self.surrogate.pats

        # Repo-only PAT cannot access org public key
        response = self.client.get("/orgs/test-org/actions/secrets/public-key",
                                     headers={"Authorization": f"token {pats.repo_write_pat()}"})
        assert response.status_code == 403

        # Repo-only PAT cannot create org secrets
        response = self.client.put("/orgs/test-org/actions/secrets/TEST",
                                     json={"encrypted_value": "test", "key_id": "123"},
                                     headers={"Authorization": f"token {pats.repo_write_pat()}"})
        assert response.status_code == 403

        # Repo-only PAT cannot delete org secrets
        response = self.client.delete("/orgs/test-org/actions/secrets/ORG_SECRET",
                                        headers={"Authorization": f"token {pats.repo_write_pat()}"})
        assert response.status_code == 403



    def test_env_public_key_repo_not_found(self):
        pats     = self.surrogate.pats
        response = self.client.get("/repos/nonexistent/repo/environments/prod/secrets/public-key",
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 404

    def test_env_public_key_env_not_found(self):
        pats     = self.surrogate.pats
        response = self.client.get("/repos/test-org/test-repo/environments/nonexistent/secrets/public-key",
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 404

    def test_create_env_secret_repo_not_found(self):
        pats     = self.surrogate.pats
        response = self.client.put("/repos/nonexistent/repo/environments/prod/secrets/SECRET",
                                     json={"encrypted_value": "test", "key_id": "123"},
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 404

    def test_create_env_secret_env_not_found(self):
        pats     = self.surrogate.pats
        response = self.client.put("/repos/test-org/test-repo/environments/nonexistent/secrets/SECRET",
                                     json={"encrypted_value": "test", "key_id": "123"},
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 404

    def test_delete_env_secret_repo_not_found(self):
        pats     = self.surrogate.pats
        response = self.client.delete("/repos/nonexistent/repo/environments/prod/secrets/SECRET",
                                        headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 404

    def test_delete_env_secret_env_not_found(self):
        pats     = self.surrogate.pats
        response = self.client.delete("/repos/test-org/test-repo/environments/nonexistent/secrets/SECRET",
                                        headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 404

    def test_get_env_secret_repo_not_found(self):
        pats     = self.surrogate.pats
        response = self.client.get("/repos/nonexistent/repo/environments/prod/secrets/SECRET",
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 404

    def test_get_env_secret_env_not_found(self):
        pats     = self.surrogate.pats
        response = self.client.get("/repos/test-org/test-repo/environments/nonexistent/secrets/SECRET",
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 404

    def test_list_env_secrets_repo_not_found(self):
        pats     = self.surrogate.pats
        response = self.client.get("/repos/nonexistent/repo/environments/prod/secrets",
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 404

    def test_create_org_secret_not_found(self):
        pats     = self.surrogate.pats
        response = self.client.put("/orgs/nonexistent-org/actions/secrets/SECRET",
                                     json={"encrypted_value": "test", "key_id": "123"},
                                     headers={"Authorization": f"token {pats.org_admin_pat()}"})
        assert response.status_code == 404

    def test_delete_org_secret_org_not_found(self):
        pats     = self.surrogate.pats
        response = self.client.delete("/orgs/nonexistent-org/actions/secrets/SECRET",
                                        headers={"Authorization": f"token {pats.org_admin_pat()}"})
        assert response.status_code == 404

    def test_get_org_secret_org_not_found(self):
        pats     = self.surrogate.pats
        response = self.client.get("/orgs/nonexistent-org/actions/secrets/SECRET",
                                     headers={"Authorization": f"token {pats.org_admin_pat()}"})
        assert response.status_code == 404

    def test_get_org_secret_not_found(self):
        pats     = self.surrogate.pats
        response = self.client.get("/orgs/test-org/actions/secrets/NONEXISTENT",
                                     headers={"Authorization": f"token {pats.org_admin_pat()}"})
        assert response.status_code == 404

    def test_get_env_secret_not_found(self):
        pats     = self.surrogate.pats
        response = self.client.get("/repos/test-org/test-repo/environments/production/secrets/NONEXISTENT",
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 404

    def test_repo_public_key_not_found(self):
        pats     = self.surrogate.pats
        response = self.client.get("/repos/nonexistent/repo/actions/secrets/public-key",
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 404

    def test_create_repo_secret_repo_not_found(self):
        pats     = self.surrogate.pats
        response = self.client.put("/repos/nonexistent/repo/actions/secrets/SECRET",
                                     json={"encrypted_value": "test", "key_id": "123"},
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 404

    def test_delete_repo_secret_repo_not_found(self):
        pats     = self.surrogate.pats
        response = self.client.delete("/repos/nonexistent/repo/actions/secrets/SECRET",
                                        headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 404

    def test_no_auth_on_various_endpoints(self):
        # Test no auth returns 401 on various endpoints
        endpoints = [
            ("GET", "/rate_limit"),
            ("GET", "/repos/test-org/test-repo/actions/secrets/public-key"),
            ("GET", "/repos/test-org/test-repo/actions/secrets"),
            ("GET", "/repos/test-org/test-repo/actions/secrets/SECRET"),
            ("GET", "/repos/test-org/test-repo/environments/production/secrets/public-key"),
            ("GET", "/repos/test-org/test-repo/environments/production/secrets"),
            ("GET", "/orgs/test-org/actions/secrets/public-key"),
            ("GET", "/orgs/test-org/actions/secrets"),
        ]

        for method, path in endpoints:
            if method == "GET":
                response = self.client.get(path)
            assert response.status_code == 401, f"Expected 401 for {method} {path}"



    def test_bearer_token_format(self):
        pats     = self.surrogate.pats
        # Test with Bearer format instead of token format
        response = self.client.get("/user", headers={"Authorization": f"Bearer {pats.admin_pat()}"})
        assert response.status_code == 200
        assert response.json()["login"] == "surrogate-admin"

    def test_raw_token_format(self):
        pats = self.surrogate.pats
        # Test with raw token (no prefix)
        response = self.client.get("/user", headers={"Authorization": pats.admin_pat()})
        assert response.status_code == 200
        assert response.json()["login"] == "surrogate-admin"

    def test_get_repo_public_key_no_auth(self):
        response = self.client.get("/repos/test-org/test-repo/actions/secrets/public-key")
        assert response.status_code == 401

    def test_get_repo_public_key_permission_denied(self):
        pats     = self.surrogate.pats
        response = self.client.get("/repos/test-org/test-repo/actions/secrets/public-key",
                                     headers={"Authorization": f"token {pats.no_scopes_pat()}"})
        assert response.status_code == 403

    def test_get_repo_secret_no_auth(self):
        response = self.client.get("/repos/test-org/test-repo/actions/secrets/EXISTING_SECRET")
        assert response.status_code == 401

    def test_get_repo_secret_permission_denied(self):
        pats     = self.surrogate.pats
        response = self.client.get("/repos/test-org/test-repo/actions/secrets/EXISTING_SECRET",
                                     headers={"Authorization": f"token {pats.no_scopes_pat()}"})
        assert response.status_code == 403

    def test_put_repo_secret_no_auth(self):
        response = self.client.put("/repos/test-org/test-repo/actions/secrets/NEW",
                                     json={"encrypted_value": "test", "key_id": "123"})
        assert response.status_code == 401

    def test_delete_repo_secret_no_auth(self):
        response = self.client.delete("/repos/test-org/test-repo/actions/secrets/EXISTING_SECRET")
        assert response.status_code == 401

    def test_delete_repo_secret_permission_denied(self):
        pats     = self.surrogate.pats
        response = self.client.delete("/repos/test-org/test-repo/actions/secrets/EXISTING_SECRET",
                                        headers={"Authorization": f"token {pats.repo_read_pat()}"})
        assert response.status_code == 403

    def test_get_env_public_key_no_auth(self):
        response = self.client.get("/repos/test-org/test-repo/environments/production/secrets/public-key")
        assert response.status_code == 401

    def test_get_env_public_key_permission_denied(self):
        pats     = self.surrogate.pats
        response = self.client.get("/repos/test-org/test-repo/environments/production/secrets/public-key",
                                     headers={"Authorization": f"token {pats.no_scopes_pat()}"})
        assert response.status_code == 403

    def test_list_env_secrets_no_auth(self):
        response = self.client.get("/repos/test-org/test-repo/environments/production/secrets")
        assert response.status_code == 401

    def test_list_env_secrets_permission_denied(self):
        pats     = self.surrogate.pats
        response = self.client.get("/repos/test-org/test-repo/environments/production/secrets",
                                     headers={"Authorization": f"token {pats.no_scopes_pat()}"})
        assert response.status_code == 403

    def test_get_env_secret_no_auth(self):
        response = self.client.get("/repos/test-org/test-repo/environments/production/secrets/ENV_SECRET")
        assert response.status_code == 401

    def test_get_env_secret_permission_denied(self):
        pats     = self.surrogate.pats
        response = self.client.get("/repos/test-org/test-repo/environments/production/secrets/ENV_SECRET",
                                     headers={"Authorization": f"token {pats.no_scopes_pat()}"})
        assert response.status_code == 403

    def test_put_env_secret_no_auth(self):
        response = self.client.put("/repos/test-org/test-repo/environments/production/secrets/NEW",
                                     json={"encrypted_value": "test", "key_id": "123"})
        assert response.status_code == 401

    def test_put_env_secret_permission_denied(self):
        pats     = self.surrogate.pats
        response = self.client.put("/repos/test-org/test-repo/environments/production/secrets/NEW",
                                     json={"encrypted_value": "test", "key_id": "123"},
                                     headers={"Authorization": f"token {pats.repo_read_pat()}"})
        assert response.status_code == 403

    def test_delete_env_secret_no_auth(self):
        response = self.client.delete("/repos/test-org/test-repo/environments/production/secrets/ENV_SECRET")
        assert response.status_code == 401

    def test_delete_env_secret_permission_denied(self):
        pats     = self.surrogate.pats
        response = self.client.delete("/repos/test-org/test-repo/environments/production/secrets/ENV_SECRET",
                                        headers={"Authorization": f"token {pats.repo_read_pat()}"})
        assert response.status_code == 403

    def test_list_org_secrets_no_auth(self):
        response = self.client.get("/orgs/test-org/actions/secrets")
        assert response.status_code == 401

    def test_org_public_key_no_auth(self):
        response = self.client.get("/orgs/test-org/actions/secrets/public-key")
        assert response.status_code == 401

    def test_get_org_secret_no_auth(self):
        response = self.client.get("/orgs/test-org/actions/secrets/ORG_SECRET")
        assert response.status_code == 401

    def test_get_org_secret_permission_denied(self):
        pats     = self.surrogate.pats
        response = self.client.get("/orgs/test-org/actions/secrets/ORG_SECRET",
                                     headers={"Authorization": f"token {pats.repo_write_pat()}"})
        assert response.status_code == 403

    def test_put_org_secret_no_auth(self):
        response = self.client.put("/orgs/test-org/actions/secrets/NEW",
                                     json={"encrypted_value": "test", "key_id": "123"})
        assert response.status_code == 401

    def test_put_org_secret_permission_denied(self):
        pats     = self.surrogate.pats
        response = self.client.put("/orgs/test-org/actions/secrets/NEW",
                                     json={"encrypted_value": "test", "key_id": "123"},
                                     headers={"Authorization": f"token {pats.repo_write_pat()}"})
        assert response.status_code == 403

    def test_delete_org_secret_no_auth(self):
        response = self.client.delete("/orgs/test-org/actions/secrets/ORG_SECRET")
        assert response.status_code == 401

    def test_delete_org_secret_permission_denied(self):
        pats     = self.surrogate.pats
        response = self.client.delete("/orgs/test-org/actions/secrets/ORG_SECRET",
                                        headers={"Authorization": f"token {pats.repo_write_pat()}"})
        assert response.status_code == 403


    def test_get_user_pat_without_user_mapping(self):
        test_pat     = self.surrogate.pats.admin_pat()                           # Add a PAT that's "known" but remove its user mapping
        user_mapping = self.surrogate.pats._users[test_pat]
        del self.surrogate.pats._users[test_pat]  # Remove user mapping

        response = self.client.get("/user", headers={"Authorization": f"token {test_pat}"})
        assert response.status_code == 401
        self.surrogate.pats._users[test_pat] = user_mapping                 # restore

    def test_get_repo_secret_repo_not_found(self):
        # Line 148: Repo doesn't exist
        pats     = self.surrogate.pats
        response = self.client.get("/repos/nonexistent/repo/actions/secrets/SOME_SECRET",
                                     headers={"Authorization": f"token {pats.admin_pat()}"})
        assert response.status_code == 404