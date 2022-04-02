from django.http import JsonResponse, HttpResponse
from django.urls import path
from django.views import View
from prometheus_client import CollectorRegistry, generate_latest, Gauge, CONTENT_TYPE_LATEST
from rest_framework.views import APIView

from monfire.client.moonfire_api import MoonfireApi
from moonfire_monitoring import settings


def get_moonfire_api():
    moonfire_api = MoonfireApi(settings.MONFIRE['BASE_URL'])
    moonfire_api.login(settings.MONFIRE['USERNAME'], settings.MONFIRE['PASSWORD'])
    return moonfire_api


class MonitorZabbix:
    @classmethod
    def urls(cls):
        return [
            path('discovery/cameras', MonitorZabbixDiscoveryCameras.as_view()),
            path('camera/<uuid:uuid>', MonitorZabbixCamera.as_view()),
        ]


class MonitorZabbixDiscoveryCameras(APIView):
    def get(self, request):
        moonfire_api = get_moonfire_api()
        try:
            basics = moonfire_api.basics()

            zabbix_data = [{
                '{#UUID}': camera['uuid'],
                '{#ID}': camera['id'],
                '{#NAME}': camera['shortName'],
            } for camera in basics['cameras']
                if 'main' in camera['streams']
            ]

            return JsonResponse({
                'data': zabbix_data
            })
        finally:
            try:
                moonfire_api.logout()
            except:
                pass


class MonitorZabbixCamera(APIView):
    def get(self, request, uuid):
        moonfire_api = get_moonfire_api()
        try:
            camera_data = moonfire_api.get_camera(str(uuid))

            stream = camera_data['streams']['main']

            # TODO
            # if stream is None:
            #     raise Exception

            return JsonResponse({
                'startTime': MoonfireApi.ts_from_90k(stream['minStartTime90k']),
                'endTime': MoonfireApi.ts_from_90k(stream['maxEndTime90k']),
                'durationTime': MoonfireApi.ts_from_90k(stream['totalDuration90k']),
            })
        finally:
            try:
                moonfire_api.logout()
            except:
                pass


class MonitorPrometheus:
    @classmethod
    def urls(cls):
        return [
            path('metrics', MonitorPrometheusMetrics.as_view()),
        ]


class MonitorPrometheusMetrics(View):
    def get(self, request):
        moonfire_api = get_moonfire_api()
        try:
            basics = moonfire_api.basics()

            registry = CollectorRegistry()

            labels_stream_names = ['camera_name', 'camera_uuid', 'stream_name', 'stream_id']

            camera_stream_recording_start_time = Gauge('camera_stream_recording_start_time', 'TODO', labelnames=labels_stream_names, registry=registry)
            camera_stream_recording_end_time = Gauge('camera_stream_recording_end_time', 'TODO', labelnames=labels_stream_names, registry=registry)
            camera_stream_recording_duration_time = Gauge('camera_stream_recording_duration_time', 'TODO', labelnames=labels_stream_names, registry=registry)
            for camera in basics['cameras']:
                for stream_name, stream in camera['streams'].items():
                    labels_stream_values = [camera['shortName'], camera['uuid'], stream_name, stream['id']]
                    camera_stream_recording_start_time.labels(*labels_stream_values).set(MoonfireApi.ts_from_90k(stream['minStartTime90k']))
                    camera_stream_recording_end_time.labels(*labels_stream_values).set(MoonfireApi.ts_from_90k(stream['maxEndTime90k']))
                    camera_stream_recording_duration_time.labels(*labels_stream_values).set(MoonfireApi.ts_from_90k(stream['totalDuration90k']))

            metrics_str = generate_latest(registry)

            return HttpResponse(metrics_str, content_type=CONTENT_TYPE_LATEST)
        finally:
            try:
                moonfire_api.logout()
            except:
                pass
