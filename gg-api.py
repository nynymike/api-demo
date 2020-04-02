#!/usr/bin/python3

from bottle import post, get, route, run, template, request, response, default_app
import json, requests, time, traceback, random, os, base64, urllib, jwt

# Change working directory so relative paths (and template lookup) work again
os.chdir(os.path.dirname(__file__))

def process_roles(header):
    role = ""
    if header != None:
        scopes = header.split(",")
        if 'manager' in scopes:
            role = 'manager'
        elif 'user' in scopes:
            role = 'user'
    return role

@post('/org')
def createOrganization():
    print("In createOrganization")
    org_id = request.forms.get('org_id')
    role = process_roles(request.headers.get('x-authenticated-scope'))
    response.status = 201
    response.content_type = 'application/json'
    result = '''{"status": "success", "role": "%s", "created": "%s"}''' % (role, org_id)
    return json.dumps(result)

@get('/org/<org_id>')
def getOrganization(org_id):
    print("In getOrganization %s" % org_id)
    role = process_roles(request.headers.get('x-authenticated-scope'))
    return '''{"status": "success", "role": "%s", "org": "%s", "active": "true"}''' % (role, org_id)

# If you are running locally
run(host='192.168.122.1', port=8081)
