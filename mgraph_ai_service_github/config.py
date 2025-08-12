from mgraph_ai_service_github import package_name

SERVICE_NAME                             = package_name
FAST_API__TITLE                          = "MGraph-AI Service GitHub"
FAST_API__DESCRIPTION                    = "Base template for MGraph-AI microservices"
LAMBDA_DEPENDENCIES__FAST_API_SERVERLESS = ['osbot-fast-api-serverless==v1.5.0']

DEPLOY__GITHUB__REPO__OWNER              = 'the-cyber-boardroom'
DEPLOY__GITHUB__REPO__NAME               = 'MGraph-AI__Service__GitHub'

ENV_VAR__GIT_HUB__ACCESS_TOKEN           = 'GIT_HUB__ACCESS_TOKEN'
