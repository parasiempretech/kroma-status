"""Public health only. No customer data, credentials or production writes."""
import base64
import json
import os
import time
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone

URL = 'https://salmon-sandpiper-345563.hostingersite.com/api/agenda?op=health'
TITLE = 'KROMA necesita revisión'


def public_read(url):
    result = subprocess.run(['curl', '--ipv4', '--fail', '--silent', '--show-error', '--location',
        '--proto', '=https', '--proto-redir', '=https', '--max-redirs', '3',
        '--connect-timeout', '8', '--max-time', '15', url], capture_output=True, timeout=20)
    if result.returncode:
        print('Comprobación pública falló:', 'agenda' if '/api/' in url else 'web', 'curl', result.returncode)
        raise RuntimeError('Public endpoint unavailable')
    return result.stdout


def healthy():
    try:
        data = json.loads(public_read(URL))
        if data.get('ok') is not True or data.get('backup', {}).get('state') != 'ok':
            print('La agenda o el backup requiere revisión')
            return False
        return b'id="root"' in public_read(URL.split('/api/')[0] + '/')
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired):
        return False


def api(path, data=None, method=None):
    body = json.dumps(data).encode() if data is not None else None
    request = urllib.request.Request('https://api.github.com/repos/' + os.environ['GITHUB_REPOSITORY'] + path,
        data=body, method=method, headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
        'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json', 'User-Agent': 'kroma-status'})
    with urllib.request.urlopen(request, timeout=15) as response:
        content = response.read()
        return json.loads(content) if content else None


def main():
    ok = False
    for attempt in range(3):
        if healthy():
            ok = True
            break
        if attempt < 2:
            time.sleep(15)
    issues = api('/issues?state=open&creator=github-actions%5Bbot%5D&per_page=100')
    incident = next((i for i in issues if i['title'] == TITLE and 'pull_request' not in i), None)
    if not ok and not incident:
        api('/issues', {'title': TITLE, 'body': 'Tres comprobaciones externas fallaron. Revisar web, agenda y estado de la copia de seguridad. No se accedió a datos de clientes. El monitor avisará aquí cuando vuelva a responder.'})
    elif ok and incident:
        api('/issues/' + str(incident['number']) + '/comments', {'body': 'Recuperado: la web, la agenda y el estado de la copia de seguridad vuelven a responder correctamente.'})
        api('/issues/' + str(incident['number']), {'state': 'closed', 'state_reason': 'completed'}, 'PATCH')
    now = datetime.now(timezone.utc)
    try:
        file = api('/contents/status.json')
        prior = json.loads(base64.b64decode(file['content']))
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
        file, prior = None, {}
    # Monthly heartbeat also keeps this scheduled repository active during healthy periods.
    if prior.get('healthy') != ok or prior.get('month') != now.strftime('%Y-%m'):
        data = {'healthy': ok, 'month': now.strftime('%Y-%m'), 'checked_at': now.isoformat()}
        payload = {'message': 'Actualizar estado del monitor', 'content': base64.b64encode(json.dumps(data, indent=2).encode()).decode()}
        if file:
            payload['sha'] = file['sha']
        api('/contents/status.json', payload, 'PUT')
    print('OK: web, agenda y backup' if ok else 'ERROR: incidente registrado')
    if not ok:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
