from pathlib import Path
from tools import vm_ingest


def test_records_contains_both_categories():
    base = Path('data_samples')
    gen = vm_ingest.records(base)
    first_five = [next(gen) for _ in range(5)]
    assert any(line.startswith('background_metric') for line in first_five)
    for line in gen:
        if line.startswith('workout_heart_rate'):
            break
    else:
        assert False, 'missing workout_heart_rate lines'


def test_send_to_vm(monkeypatch):
    captured = {}

    if vm_ingest.HAVE_REQUESTS:
        def fake_post(url, data):
            captured['url'] = url
            captured['data'] = data
            class Resp:
                def raise_for_status(self):
                    pass
            return Resp()
        monkeypatch.setattr(vm_ingest.requests, 'post', fake_post)
    else:
        def fake_urlopen(req):
            captured['url'] = req.full_url
            captured['data'] = req.data.decode('utf-8')
            class Resp:
                def __enter__(self):
                    return self
                def __exit__(self, exc_type, exc, tb):
                    pass
                def read(self):
                    return b''
            return Resp()
        monkeypatch.setattr(vm_ingest.urllib.request, 'urlopen', fake_urlopen)

    vm_ingest.send_to_vm(Path('data_samples'), base_url='http://vm')
    assert captured['url'] == 'http://vm/write'
    assert captured['data'].splitlines()[0].startswith('background_metric')
