#!/usr/bin/env python3
import urllib.request, urllib.parse, json, base64, os, time

ci = os.environ['CLIENT_ID']
cs = os.environ['CLIENT_SECRET']

# Step 1: Get device code
data = urllib.parse.urlencode({
    'client_id': ci,
    'scope': 'https://www.googleapis.com/auth/youtube.upload'
}).encode()
req = urllib.request.Request('https://oauth2.googleapis.com/device/code', data=data)
resp = urllib.request.urlopen(req, timeout=30)
result = json.loads(resp.read())

dc = result['device_code']
uc = result['user_code']
vu = result['verification_url']

print('=' * 50)
print('OPEN THIS URL IN YOUR BROWSER:')
print(vu)
print('=' * 50)
print('ENTER THIS CODE:', uc)
print('=' * 50)
print('CLICK ALLOW, THEN WAIT...')
print('=' * 50)

with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
    f.write(f'verification_url={vu}\n')
    f.write(f'user_code={uc}\n')
    f.write(f'device_code={dc}\n')

# Step 2: Poll for token
for i in range(60):
    time.sleep(5)
    
    data = urllib.parse.urlencode({
        'client_id': ci,
        'client_secret': cs,
        'code': dc,
        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
    }).encode()
    
    req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data)
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read())
    
    if 'access_token' in result:
        at = result['access_token']
        rt = result.get('refresh_token', '')
        
        cred = {
            'access_token': at,
            'refresh_token': rt,
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': ci,
            'client_secret': cs,
            'expiry': '2026-07-12T00:00:00Z'
        }
        
        cred_b64 = base64.b64encode(json.dumps(cred).encode()).decode()
        
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(f'cred_base64={cred_b64}\n')
            f.write('status=success\n')
        
        print('=' * 50)
        print('AUTHORIZATION SUCCESS!')
        print('CREDENTIALS_BASE64:')
        print(cred_b64)
        print('=' * 50)
        exit(0)
    
    err = result.get('error', 'unknown')
    if err != 'authorization_pending':
        print(f'Error: {err}')
        exit(1)
    
    print(f'Waiting ({i+1}/60)...')

print('TIMEOUT - no authorization in 5 minutes')
exit(1)
