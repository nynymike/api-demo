# Using OAuth to implement RBAC

## Overview

Using roles to control access to resources makes sense for lots of
security use cases. One benefit of RBAC is that it's deterministic--
from an audit perspective, you can tell who had access to what at any point
in time. This is harder to achieve when contextual variables
play a role in determining access.

In this simple demo, we use the OAuth scopes of an access token to represent
the roles of the person. The demo launches a very simple website that calls an
API on behalf of a person. The website presents an access token obtained during
the OpenID Connect authentication flow (i.e. when the person logged in).

To develop this demo, we used the
[Bottle Python Web Framework](https://bottlepy.org/docs/dev/).
It provides both the website, and the API. For web applications, the Gluu Server
requires ssl for the redirect_uri; in the demo we use Apache web server.
Substitute another web server if you prefer.

For testing, we created two users in the Gluu Server: one with the user claim for
role with the value of `manager`, and one `user`. The demo has just one endpoint:
`/org`. The demo configures the Gluu Gateway to allow the user with the `manager`
role to perform both a GET and POST on the `/org` endpoint, while the `user` role
only enables the user to perform a GET.

Initially, the scope value for the access token will contain only the
OpenID scopes, for example, `openid`, `profile`, and `email`. What would make
this job easy is if we could add scope values to the access token called
"manager" or "user", corresponding to the `role` user claim  provisioned for
the person's account. The demo shows you how to do this in the Gluu Server by
using the custom script for Introspection.

This demo has instructions for Ubuntu 18. If you want to use another
linux distribution or docker, adjust some of the commands accordingly.

### Server 1: Install Gluu Server 4.1

```
# echo "deb https://repo.gluu.org/ubuntu/ bionic-devel main" > /etc/apt/sources.list.d/gluu-repo.list
# curl https://repo.gluu.org/ubuntu/gluu-apt.key | apt-key add -
# apt update
# apt install gluu-server
# apt install gluu-gateway
# /sbin/gluu-serverd start
# /sbin/gluu-serverd login
# cd install/community-edition-setup/
# ./setup.py
           ... See Gluu Server docs for more instructions ...
```
Login Gluu Server admin website

* Copy/Paste the `gluu_server_introspection_script.py`
* Add two test users

### Server 2: Install Gluu Gateway 4.1

```
# echo "deb https://repo.gluu.org/ubuntu/ bionic-devel main" > /etc/apt/sources.list.d/gluu-repo.list
# curl https://repo.gluu.org/ubuntu/gluu-apt.key | apt-key add -
# apt update
# apt install gluu-gateway
```

Make a tunnel to the Gluu Gateway Server so you can get to the admin console.

```
 $ ssh -L 1338:localhost:1338 gg.gluu.me
```

Login to Gluu Gateway admin interface

* Configure Service
* Configure route
* Add OAuth plugin

* Follow [instructions](.) for Gluu Gateway configuration

### Server 3: Install Apache2 and Bottle Web Framework

```
# apt install python3, pip3, apache2,
# pip3 install bottle, requests
# a2enmod ssl
# openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
         -keyout /etc/ssl/private/apache-selfsigned.key \
         -out /etc/ssl/certs/apache-selfsigned.crt
```

* Update `/etc/apache2/sites-available/default-ssl.conf`:

```
   SSLCertificateFile      /etc/ssl/certs/apache-selfsigned.crt
   SSLCertificateKeyFile /etc/ssl/private/apache-selfsigned.key

```

Add a proxy to the Bottle server

```
   ProxyPass / http://0.0.0.0:8080/
   ProxyPassReverse / http://0.0.0.0:8080/
```

* Restart Apache:

```
# systemctl restart apache2

```

* Make a tunnel from the Web server to the Gluu Gateway Server, so it can
call the Kong admin API (this is a quick fix... or you can open the firewall
  port and make sure Kong listens on an ethernet interface)

```
ssh -L 8001:localhost:8001 mike@gg.gluu.me
```

* Get ssl certificates for Gluu Server and Kong; cat into one file
called certs.pem. Note: you may have to use `dos2unix` to remove the
carriage returns (^M).

* Run bottle application


### Testing

* Navigate to the web server.
* Login and try Create / Get depending on what user you are testing
* It doesn't matter what number you enter
