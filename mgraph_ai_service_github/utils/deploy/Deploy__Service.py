from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency                          import Lambda__Dependency
from osbot_aws.aws.lambda_.schemas.Schema__Lambda__Dependency__Local_Install__Data  import Schema__Lambda__Dependency__Local_Install__Data
from osbot_fast_api_serverless.deploy.Deploy__Serverless__Fast_API                  import Deploy__Serverless__Fast_API
from osbot_utils.helpers.duration.decorators.capture_duration                       import capture_duration
from osbot_utils.utils.Env                                                          import get_env
from mgraph_ai_service_github.config                                                import SERVICE_NAME, LAMBDA_DEPENDENCIES__FAST_API_SERVERLESS, ENV_VAR__SERVICE__AUTH__PRIVATE_KEY, ENV_VAR__SERVICE__AUTH__PUBLIC_KEY
from mgraph_ai_service_github.fast_api.lambda_handler                               import run

RUNTIME_TO_ABI = {
        "3.12": ("312", "cp312"),
        "3.11": ("311", "cp311"),
        "3.10": ("310", "cp310"),
        "3.9": ("39", "cp39"),
    }

class Deploy__Service(Deploy__Serverless__Fast_API):

    def deploy_lambda(self):
        with super().deploy_lambda() as _:
            # Add any service-specific environment variables here
            _.set_env_variable(ENV_VAR__SERVICE__AUTH__PUBLIC_KEY , get_env(ENV_VAR__SERVICE__AUTH__PUBLIC_KEY))
            _.set_env_variable(ENV_VAR__SERVICE__AUTH__PRIVATE_KEY, get_env(ENV_VAR__SERVICE__AUTH__PRIVATE_KEY))
            return _

    def handler(self):
        return run

    def lambda_dependencies(self):
        return LAMBDA_DEPENDENCIES__FAST_API_SERVERLESS

    def lambda_name(self):
        return SERVICE_NAME

    # todo: apply the code changes below to OSBot_Utils
    #     the code below patches this patches a bug in Lambda__Dependency which was failing to build locally the (pynacl==1.5.0)
    def upload_lambda_dependencies_to_s3(self):
        upload_results = {}
        for package_name in self.lambda_dependencies():
            with Lambda__Dependency(package_name=package_name) as _:
                self.lambda_dependency = _                                      # capture this object so that we can use it below
                _.dependency__local.install = self.install                      # monkey patch this function with the method below
                upload_results[package_name] = _.install_and_upload()           # this will call .install()
        return upload_results



    def lambda_flags(self, runtime: str):
        py, abi = RUNTIME_TO_ABI[runtime]
        return [ '--platform'       , 'manylinux2014_x86_64',
                 '--implementation' , 'cp'                  ,
                 '--python-version' , py                    ,
                 '--abi'            , abi                   ]

    def install(self): # this is a method from self.lambda_dependency.dependency__local
        from osbot_utils.utils.Process import Process
        lambda_runtime = '3.11'
        lambda_flags = self.lambda_flags(lambda_runtime)
        self = self.lambda_dependency.dependency__local
        local_install_data = self.install__data()               # failing here, method is executed but this is lost

        needs_install = False
        if local_install_data is None:
            needs_install = True
        else:
            if 'error' in local_install_data.install_data.get('stderr','').lower():
                needs_install = True

        if needs_install:                          # at the moment it is none (it shouldn't be)
            with capture_duration() as duration__install:
                target_path = self.path()
                args = ['install']
                from osbot_utils.utils.Dev import pprint
                pprint(args)
                if self.target_aws_lambda:
                    lambda_runtime = '3.12'
                    args.extend([*lambda_flags, '--only-binary=:all:'])         # todo: these lambda flags (python version dependent, are what will need to be added to the OSBot_AWS code base
                args.extend(['-t', target_path, self.package_name])
                install_data  = Process.run('pip3', args)
                installed_files = self.files()
            kwargs = dict(package_name       = self.package_name        ,
                          target_path        = target_path              ,
                          install_data       = install_data             ,
                          installed_files    = installed_files          ,
                          duration           = duration__install.seconds)

            local_install_data = Schema__Lambda__Dependency__Local_Install__Data (**kwargs)
            self.install__data__save(local_install_data)
        return local_install_data

