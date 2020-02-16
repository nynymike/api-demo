#!/usr/bin/python3
# export REQUESTS_CA_BUNDLE=/home/mike/Github/api-demo/gs.pem

from bottle import post, get, route, run, template, request
import json, requests, time, traceback, random, os, base64, urllib, jwt

client = None
op_host = "gs.gluu.me"
gg_host = "gg.gluu.me"
callback_host = "king.gluu.me"
now = int(time.time())
registration_endpoint = "https://%s/oxauth/restv1/register" % op_host
authorization_endpoint = "https://%s/oxauth/restv1/authorize" % op_host
token_endpoint = "https://%s/oxauth/restv1/token" % op_host
userinfo_endpoint = "https://%s/oxauth/restv1/userinfo" % op_host
introspection_endpoint = "https://%s/oxauth/restv1/introspection" % op_host
callback_uri = "https://%s/callback" % callback_host
orgEndpoint = "https://%s/junction/organization" % gg_host
itemEndpoint = "https://%s/junction/item" % gg_host

@route('/')
@route('/hello/<name>')
def index(name='Stranger'):
    return template('<b>Hello {{name}}</b>!', name=name)

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
    state = request.query.state
    if (code == None) or (state == None):
        return '''
        <H1>Code and state must be present!</H1>
        <UL>
            <LI>code: %s</LI>
            <LI>state: %s </LI>
        </UL>
        ''' % (code, state)

    return_html = '''
        <H1>Callback Response</H1>
        <UL>
          <LI>code = %s</LI>
          <LI>state = %s</LI>
        <UL>
    ''' % (code, state)

#    tokens = get_tokens(code, op_state)
#    return_html = return_html + '''
#            <H1>Tokens</H1>
#            <UL>
#              <LI>access token = %s</LI>
#              <LI>id_token = %s</LI>
#            <UL>
#            <H1>Next Step: Call Userinfo</H1>
#            <UL>
#                <A HREF="/userinfo">Click here to get UserInfo</A>
#            </UL>
#        ''' % (tokens['access_token'], tokens['id_token'])

    return return_html

@route('/userinfo')
def get_userinfo():
    headers = {'Content-Type': 'application/json',
                'Authorization': 'Bearer %s' % tokens['access_token']}
    try:
        r = requests.get(url=userinfo_endpoint, headers=headers)
        if r.status_code != 200:
            print("Userinfo Error! Return Code %i" % r.status_code)
            return '''
                <H1>Userinfo Error! Return Code %i" % r.status_code)
            '''
        userinfo = r.json()
    except:
        print(traceback.format_exc())
    print("Userinfo: %s" % str(userinfo))
    return '''
        <H1>Userinfo</H1>
        <UL>
          <LI>UserInfo = %s</LI>
        <UL>
        <H1>Next Step: Call APIs</H1>
        <UL>
            <A HREF="/userinfo">GET Organization</A>
        </UL>
        <UL>
            <A HREF="/userinfo">POST Organization</A>
        </UL>
        <UL>
            <A HREF="/userinfo">GET Item</A>
        </UL>
        <UL>
            <A HREF="/userinfo">POST Item</A>
        </UL>
    ''' % str(userinfo)

@get('/organization')
def getOrganization():
    return True

@post('/organization')
def createOrganization():
    return True

@get('/item')
def getOrganization():
    return True

@post('/item')
def createOrganization():
    return True

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

def get_tokens(code, state):
    headers = {'Content-Type': 'application/json'}
    claims = {
        "code": code,
        "state": state,
        "client_id": client['client_id'],
        "client_secret": client['client_secret']
    }
    try:
        r = requests.post(url=token_endpoint,
                          json=claims,
                          headers=headers)
        if r.status_code != 200:
            print("Token Error! Return Code %i" % r.status_code)
            return None
        tokens = r.json()
    except:
        print(traceback.format_exc())
    print("Tokens: %s" % str(token))
    return tokens

def introspect_token():
    return ""

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
        print(traceback.format_exc())
    print("Client: %s" % str(client))
    return client

client = register_client()
run(host='localhost', port=8080)
