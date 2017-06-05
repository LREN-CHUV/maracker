from microbadger_service import MicrobadgerService

if __name__ == "__main__":
    print(MicrobadgerService.get_docker_metadata('hbpmip', 'portal-backend'))
    print(MicrobadgerService.get_docker_metadata('toto', 'portal-backend'))

