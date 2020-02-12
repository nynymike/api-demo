from bottle import post, get, route, run, template, request
import json, requests, time, traceback, random, os, base64, urllib, jwt

now = int(time.time())
request_object = None
state = None
nonce = None
registration_endpoint = "https://mike-test.gluu.org/oxauth/restv1/register"
authorization_endpoint = "https://mike-test.gluu.org/oxauth/restv1/authorize"
callback_uri = "http://localhost:8080/callback"

@route('/')
@route('/hello/<name>')
def index(name='Stranger'):
    return template('<b>Hello {{name}}</b>!', name=name)

@route('/')
@get('/login')
def login():
    return '''
        <form action="%s" method="post">
            <input value="Login" type="submit" />
        </form>
    ''' % "%s?request=%s" % (authorization_endpoint, get_authz_request_object())

@route('/callback')
def callback():
    code = request.forms.get('code')
    op_state = request.forms.get('state')
    return '''
        <UL>
          <LI>code = %s</LI>
          <LI>state = %s</LI>
        <UL>
    ''' % (code, op_state)

def check_login(username, password):
    return True

def get_authz_request_object():
    state = base64.b64encode(os.urandom(18)).decode()
    nonce =  base64.b64encode(os.urandom(18)).decode()
    request_object = {  "scope": "openid",
                        "response_type": "code",
                        "client_id": client['client_id'],
                        "client_secret": client['client_secret'],
                        "redirect_uri": callback_uri,
                        "state": state,
                        "nonce": nonce
    }
    print("Request Object:\n%s\n" % str(request_object))
    return urllib.parse.quote(jwt.encode(request_object, None, "none"))

def register_client():
    client = None

    claims = {
       "application_type": "web",
       "redirect_uris": [callback_uri],
       "client_name": "Bottle Client %s" % now,
       "subject_type": "pairwise",
       "grant_types": ["authorization_code"],
       "respone_types": ["code"],
       "scope": "openid",
       "token_endpoint_auth_method": "client_secret_basic"
    }
    headers = {'Content-Type': 'application/json'}
    try:
        r = requests.post(url=registration_endpoint,
                                 json=claims,
                                 headers=headers)
        if r.status_code != 200:
            print("Client Error! Return Code %i" % r.status_code)
            return None
        client = r.json()
    except:
        print(traceback.format_exc())
    print("Client: %s" % str(client))
    return client

client = register_client()
run(host='localhost', port=8080)
