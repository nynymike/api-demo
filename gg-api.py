#!/usr/bin/python3

from bottle import post, get, route, run, template, request, response, default_app
import json, requests, time, traceback, random, os, base64, urllib, jwt

# Change working directory so relative paths (and template lookup) work again
os.chdir(os.path.dirname(__file__))

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

# If you are running locally
run(host='192.168.122.1', port=8081)
