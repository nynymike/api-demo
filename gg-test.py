#!/usr/bin/python3

from bottle import post, get, route, run, template, request, response, default_app
import json, requests, time, traceback, random, os, base64, urllib, jwt

# Change working directory so relative paths (and template lookup) work again
os.chdir(os.path.dirname(__file__))

client = None
op_host = "gs.gluu.me"
gg_host = "gg.gluu.me"
callback_host = "king.gluu.me"
now = int(time.time())
registration_endpoint = "https://%s/oxauth/restv1/register" % op_host
authorization_endpoint = "https://%s/oxauth/restv1/authorize" % op_host
token_endpoint = "https://%s/oxauth/restv1/token" % op_host
callback_uri = "https://%s/callback" % callback_host
orgEndpoint = "https://%s/org" % gg_host
kongAPI = "http://localhost:8001"

@route('/')
@get('/login')
def login():
    request_params = ""
    request_object = get_authz_request_object()
    input = '\t\t\t\t<input type="hidden" name="%s" value="%s" />\n'
    for param in request_object.keys():
        request_params = request_params + input % (param, request_object[param])
    return '''
        <h1>Welcome to the Gluu Gateway Demo</H1>
        <p>This application was written using the Python Bottle Framework.</p>
        <form action="%s" method="post">
            %s
            <input value="Login" type="submit" />
        </form>
    ''' % (authorization_endpoint, request_params)

@route('/callback')
def callback():
    code = request.query.code
    if not code:
        return "<H1>Code note found!</H1>"

    tokens = get_tokens(code)
    access_token = None
    if 'access_token' in tokens:
        access_token = tokens['access_token']
    else:
        return "<H1>Access token not found!</H1>"

    return '''
        <H1>Test Gluu Gateway</H1>
        <FORM action="/callAPI" method="post">
            <input type="radio" name="testAction" value="create" checked> Create<br>
            <input type="radio" name="testAction" value="lookup"> Lookup<br>
            Organization Identifier <input name="org_id"><br/>
            <input name="access_token" type="hidden" value=%s /><br/>
            <input value="Call API" type="submit" />
        </FORM>
        ''' % access_token

@post('/callAPI')
def callAPI():
    r = None
    testAction = request.forms.get('testAction')
    org_id = request.forms.get('org_id')
    params = {"org_id": org_id}
    headers = {"Authorization": "Bearer %s" % request.forms.get('access_token')}
    if testAction == "create":
        try:
            print("\nPOST %s\nParams: %s\n" % (orgEndpoint, str(params)))
            r = requests.post(url=orgEndpoint, headers=headers, data=params)
        except:
            print(traceback.format_exc())
            return("Error Calling API!")
    elif testAction == "lookup":
        try:
            lookupUrl = "%s/%s" % (orgEndpoint, org_id)
            print("\nGET %s\n" % lookupUrl)
            r = requests.get(url=lookupUrl, headers=headers)
        except:
            print(traceback.format_exc())
            return("Error Calling API!")

    if r.status_code not in [200, 201]:
        return "<H1>Access Denied: status code %s</H1>" % r.status_code
    return r.json()

@post('/org')
def createOrganization():
    print("In createOrganization")
    org_id = request.forms.get('org_id')
    response.status = 201
    response.content_type = 'application/json'
    result = '''{"status": "success", "created": "%s"}''' % org_id
    return json.dumps(result)

@get('/org/<org_id>')
def getOrganization(org_id):
    print("In getOrganization %s" % org_id)
    return '''{"status": "success", "org": "%s", "active": "true"}''' % org_id

def get_authz_request_object(returnJWT=False):
    state = base64.b64encode(os.urandom(18)).decode()
    nonce =  base64.b64encode(os.urandom(18)).decode()
    request_object = {  "scope": "openid",
                        "response_type": "code",
                        "client_id": client['client_id'],
                        "client_secret": client['client_secret'],
                        "redirect_uri": callback_uri,
                        "response_type": "code",
                        "state": state,
                        "nonce": nonce
    }
    print("Request Object:\n%s\n" % str(request_object))
    if returnJWT:
        return urllib.parse.quote(jwt.encode(request_object, None, "none"))
    else:
        return request_object

def get_tokens(code):
    tokens = None
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    creds = requests.auth.HTTPBasicAuth(client['client_id'], client['client_secret'])
    params = {
        "code": code,
        "grant_type": "authorization_code",
        "client_id": client['client_id'],
        "redirect_uri": callback_uri
    }
    try:
        r = requests.post(url=token_endpoint,
                          data=params,
                          headers=headers,
                          auth=creds)
        if r.status_code != 200:
            print("Token Error! Return Code %i" % r.status_code)
            print(r.json())
            return None
        tokens = r.json()
    except:
        print(traceback.format_exc())
    print("Tokens: %s\n" % str(tokens))
    return tokens

def register_client():
    claims = {
       "application_type": "web",
       "redirect_uris": [callback_uri],
       "client_name": "Bottle Client %s" % now,
       "subject_type": "pairwise",
       "grant_types": ["authorization_code"],
       "respone_types": ["code"],
       "scope": "openid",
       'request_object_signing_alg': "none",
       "token_endpoint_auth_method": "client_secret_basic"
    }
    headers = {'Content-Type': 'application/json'}
    try:
        r = requests.post(url=registration_endpoint,
                                 json=claims,
                                 headers=headers)
        if r.status_code != 200:
            print("Client Error! Return Code %i" % r.status_code)
            print(r.json())
            return None
        client = r.json()
    except:
        print("Error registering client.\n")
        print(traceback.format_exc())
    print("Client: %s" % str(client))
    return client

def add_kong_consumer():
    kongConsumerEndpoint = "%s/consumers" % kongAPI
    headers = {'Content-Type': 'application/json'}
    claims = {"custom_id": client['client_id'],
              "username": client['client_name']}
    try:
        r = requests.post(url=kongConsumerEndpoint,
                          json=claims,
                          headers=headers)
        if r.status_code != 201:
            print("Error adding Kong Consumer %i" % r.status_code)
            print(r.json())
            return None
        else:
            print("\nAdded Kong Consumer: %s\n" % client['client_name'])
    except:
        print(traceback.format_exc())

client = register_client()
add_kong_consumer()

# If you are running locally
run(host='localhost', port=8080)

# If you are running via Apache WSGI
# default_app()
