from unittest                                                                            import TestCase
from mgraph_ai_service_github.surrogates.github.schemas.Schema__Surrogate__Rate_Limit    import Schema__Surrogate__Rate_Limit


class test__Schema__Surrogate__Rate_Limit(TestCase):

    def test_decrement(self):
        rate_limit = Schema__Surrogate__Rate_Limit(limit=5000, remaining=4999, used=1)

        rate_limit.decrement()

        assert rate_limit.remaining == 4998
        assert rate_limit.used      == 2

    def test_decrement_at_zero(self):
        rate_limit = Schema__Surrogate__Rate_Limit(limit=5000, remaining=0, used=5000)

        rate_limit.decrement()

        assert rate_limit.remaining == 0                                                # Should not go negative
        assert rate_limit.used      == 5001

    def test_to_github_response(self):
        rate_limit = Schema__Surrogate__Rate_Limit(limit=5000, remaining=4500, reset=1234567890, used=500)

        response = rate_limit.to_github_response()

        assert response == {'rate': {'limit': 5000, 'remaining': 4500, 'reset': 1234567890, 'used': 500}}

