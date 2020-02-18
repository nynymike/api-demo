from org.gluu.model.custom.script.type.introspection import IntrospectionType
from java.lang import String
from org.gluu.oxauth.service import UserService
from org.gluu.oxauth.model.common import User
from org.gluu.service.cdi.util import CdiUtil

class Introspection(IntrospectionType):
    def __init__(self, currentTimeMillis):
        self.currentTimeMillis = currentTimeMillis

    def init(self, configurationAttributes):
        print "Introspection script. Initializing ..."
        print "Introspection script. Initialized successfully"
        return True

    def destroy(self, configurationAttributes):
        print "Introspection script. Destroying ..."
        print "Introspection script. Destroyed successfully"
        return True

    def getApiVersion(self):
        return 1

    # Returns boolean, true - apply introspection method, false - ignore it.
    # This method is called after introspection response is ready. This method can modify introspection response.
    # Note :
    # responseAsJsonObject - is org.codehaus.jettison.json.JSONObject, you can use any method to manipulate json
    # context is reference of org.gluu.oxauth.service.external.context.ExternalIntrospectionContext (in https://github.com/GluuFederation/oxauth project, )
    def modifyResponse(self, responseAsJsonObject, context):
        userService = CdiUtil.bean(UserService)
        print "-->userService: " + userService.toString()
        grant = context.getGrantOfIntrospectionToken()
        if grant:
            print "-->grant: " + grant.toString()
        else:
            print "-->grant: is null"
        user = grant.getUser()
        if user:
            print "-->user: " + user.toString()
        else:
            print "-->user: is null"
        role = userService.getCustomAttribute(user, "role")
        if role == None:
             return None
        else:
            role = role.getValue()
        print "User Role: " + user_role
        if user_role == "admin":
            responseAsJsonObject.accumulate("scope", "admin")
        if user_role == "user":
            responseAsJsonObject.accumulate("scope", "user")
        return True
