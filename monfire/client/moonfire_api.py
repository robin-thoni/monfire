import requests


class MoonfireApi:
    @staticmethod
    def ts_to_90k(ts: int) -> int:
        return ts * 90000

    @staticmethod
    def ts_from_90k(v: int) -> int:
        return v // 90000

    def __init__(self, base_url: str):
        self.api_url = '{base_url}/api'.format(base_url=base_url.rstrip('/'))
        self.session = requests.Session()
        self.csrf = None

    def login(self, username: str, password: str) -> None:
        r = self.session.post('{api_url}/login'.format(api_url=self.api_url), json={
            'username': username,
            'password': password,
        })
        r.raise_for_status()

    def logout(self):
        r = self.session.post('{api_url}/logout'.format(api_url=self.api_url), json={
            'csrf': self.csrf
        })
        r.raise_for_status()

    def basics(self, days=False, camera_configs=False):
        r = self.session.get('{api_url}/'.format(api_url=self.api_url), params={
            'days': days,
            'cameraConfigs': camera_configs,
        })
        r.raise_for_status()

        basics = r.json()

        self.csrf = basics['user']['session']['csrf']

        return basics

    def get_camera(self, uuid: str):
        r = self.session.get('{api_url}/cameras/{uuid}/'.format(api_url=self.api_url, uuid=uuid))
        r.raise_for_status()

        return r.json()
