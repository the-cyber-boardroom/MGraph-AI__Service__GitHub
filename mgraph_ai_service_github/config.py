from mgraph_ai_service_github import package_name

SERVICE_NAME                             = package_name
FAST_API__TITLE                          = "MGraph-AI Service GitHub"
FAST_API__DESCRIPTION                    = "Base template for MGraph-AI microservices"
LAMBDA_DEPENDENCIES__FAST_API_SERVERLESS = ['osbot-fast-api-serverless==v1.31.0', 'pynacl==1.6.1']

DEPLOY__GITHUB__REPO__OWNER              = 'the-cyber-boardroom'
DEPLOY__GITHUB__REPO__NAME               = 'MGraph-AI__Service__GitHub'

ENV_VAR__GIT_HUB__ACCESS_TOKEN           = 'GIT_HUB__ACCESS_TOKEN'
ENV_VAR__SERVICE__AUTH__PRIVATE_KEY      = 'SERVICE__AUTH__PRIVATE_KEY'
ENV_VAR__SERVICE__AUTH__PUBLIC_KEY       = 'SERVICE__AUTH__PUBLIC_KEY'

