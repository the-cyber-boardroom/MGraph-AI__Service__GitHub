import pytest
from osbot_utils.utils.Env                                   import load_dotenv, get_env
from mgraph_ai_service_github.utils.testing.QA__HTTP_Client  import ENV_VAR__GIT_HUB__SERVICE__URL, DEFAULT__SERVICE__URL, ENV_VAR__GIT_HUB__ACCESS_TOKEN


def pytest_configure(config):                                                       # Load .env file before running tests
    load_dotenv()


def pytest_collection_modifyitems(config, items):                                   # Add markers based on test requirements
    service_url = get_env(ENV_VAR__GIT_HUB__SERVICE__URL, DEFAULT__SERVICE__URL)
    github_pat  = get_env(ENV_VAR__GIT_HUB__ACCESS_TOKEN, '')

    skip_no_service = pytest.mark.skip(reason=f"No service URL configured ({ENV_VAR__GIT_HUB__SERVICE__URL})")
    skip_no_pat     = pytest.mark.skip(reason=f"No GitHub PAT configured ({ENV_VAR__GIT_HUB__ACCESS_TOKEN})")

    for item in items:
        if 'qa' in item.nodeid:                                                     # Only QA tests
            if not service_url:
                item.add_marker(skip_no_service)

            if 'github_pat' in item.name.lower() and not github_pat:
                item.add_marker(skip_no_pat)


@pytest.fixture(scope='session')
def service_url():                                                                  # Fixture providing service URL
    load_dotenv()
    return get_env(ENV_VAR__GIT_HUB__SERVICE__URL, DEFAULT__SERVICE__URL)


@pytest.fixture(scope='session')
def github_pat():                                                                   # Fixture providing GitHub PAT
    load_dotenv()
    return get_env(ENV_VAR__GIT_HUB__ACCESS_TOKEN, '')
