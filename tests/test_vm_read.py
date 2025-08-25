from pathlib import Path
from tools import vm_ingest


def test_read_background_metric(monkeypatch):
    captured = {}
    metric_value = "123"

    if vm_ingest.HAVE_REQUESTS:
        def fake_post(url, data):
            captured['post_url'] = url
            class Resp:
                def raise_for_status(self):
                    pass
            return Resp()
        monkeypatch.setattr(vm_ingest.requests, 'post', fake_post)

        def fake_get(url, params):
            captured['get_url'] = url
            captured['get_query'] = params['query']
            class Resp:
                def raise_for_status(self):
                    pass
                def json(self):
                    return {"data": {"result": [{"value": [0, metric_value]}]}}
            return Resp()
        monkeypatch.setattr(vm_ingest.requests, 'get', fake_get)
    else:
        import urllib.parse

        def fake_urlopen(req):
            if hasattr(req, 'full_url'):
                captured['post_url'] = req.full_url
                class Resp:
                    def __enter__(self):
                        return self
                    def __exit__(self, exc_type, exc, tb):
                        pass
                    def read(self):
                        return b''
                return Resp()
            parsed = urllib.parse.urlsplit(req)
            captured['get_url'] = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            captured['get_query'] = urllib.parse.parse_qs(parsed.query)['query'][0]
            class Resp:
                def __enter__(self):
                    return self
                def __exit__(self, exc_type, exc, tb):
                    pass
                def read(self):
                    return ("{\"data\":{\"result\":[{\"value\":[0,\"" + metric_value + "\"]}]}}" ).encode('utf-8')
            return Resp()
        monkeypatch.setattr(vm_ingest.urllib.request, 'urlopen', fake_urlopen)

    vm_ingest.send_to_vm(Path('data_samples'), base_url='http://vm')
    value = vm_ingest.read_metric('http://vm', 'background_metric')
    assert captured.get('post_url') == 'http://vm/write'
    assert captured.get('get_url') == 'http://vm/api/v1/query'
    assert captured.get('get_query') == 'background_metric'
    assert value == float(metric_value)


def test_read_workout_metric(monkeypatch):
    captured = {}
    metric_value = "87"

    if vm_ingest.HAVE_REQUESTS:
        def fake_post(url, data):
            captured['post_url'] = url
            class Resp:
                def raise_for_status(self):
                    pass
            return Resp()
        monkeypatch.setattr(vm_ingest.requests, 'post', fake_post)

        def fake_get(url, params):
            captured['get_url'] = url
            captured['get_query'] = params['query']
            class Resp:
                def raise_for_status(self):
                    pass
                def json(self):
                    return {"data": {"result": [{"value": [0, metric_value]}]}}
            return Resp()
        monkeypatch.setattr(vm_ingest.requests, 'get', fake_get)
    else:
        import urllib.parse

        def fake_urlopen(req):
            if hasattr(req, 'full_url'):
                captured['post_url'] = req.full_url
                class Resp:
                    def __enter__(self):
                        return self
                    def __exit__(self, exc_type, exc, tb):
                        pass
                    def read(self):
                        return b''
                return Resp()
            parsed = urllib.parse.urlsplit(req)
            captured['get_url'] = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            captured['get_query'] = urllib.parse.parse_qs(parsed.query)['query'][0]
            class Resp:
                def __enter__(self):
                    return self
                def __exit__(self, exc_type, exc, tb):
                    pass
                def read(self):
                    return ("{\"data\":{\"result\":[{\"value\":[0,\"" + metric_value + "\"]}]}}" ).encode('utf-8')
            return Resp()
        monkeypatch.setattr(vm_ingest.urllib.request, 'urlopen', fake_urlopen)

    vm_ingest.send_to_vm(Path('data_samples'), base_url='http://vm')
    value = vm_ingest.read_metric('http://vm', 'workout_heart_rate')
    assert captured.get('post_url') == 'http://vm/write'
    assert captured.get('get_url') == 'http://vm/api/v1/query'
    assert captured.get('get_query') == 'workout_heart_rate'
    assert value == float(metric_value)
