import pytest
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate            import GitHub__API__Surrogate

class test__GitHub__API__Surrogate:
    
    def test_setup(self):
        surrogate = GitHub__API__Surrogate().setup()
        
        assert surrogate.state  is not None
        assert surrogate.pats   is not None
        assert surrogate.keys   is not None
        assert surrogate.routes is not None
        assert surrogate.app()  is not None
    
    def test_fluent_test_data(self):
        surrogate = (GitHub__API__Surrogate()
                     .setup()
                     .add_repo("test-org", "test-repo")
                     .add_environment("test-org", "test-repo", "production")
                     .add_secret("test-org", "test-repo", "API_KEY")
                     .add_env_secret("test-org", "test-repo", "production", "DB_PASS")
                     .add_org("test-org")
                     .add_org_secret("test-org", "ORG_TOKEN"))
        
        # Verify state
        assert surrogate.state.repo_exists("test-org", "test-repo")
        assert surrogate.state.environment_exists("test-org", "test-repo", "production")
        assert surrogate.state.get_repo_secret("test-org", "test-repo", "API_KEY") is not None
        assert surrogate.state.get_env_secret("test-org", "test-repo", "production", "DB_PASS") is not None
        assert surrogate.state.get_org_secret("test-org", "ORG_TOKEN") is not None
    
    def test_reset(self):
        surrogate = (GitHub__API__Surrogate()
                     .setup()
                     .add_repo("owner", "repo")
                     .add_secret("owner", "repo", "KEY"))
        
        surrogate.reset()
        
        assert surrogate.state.repo_exists("owner", "repo") is False



