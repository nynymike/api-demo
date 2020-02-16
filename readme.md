# Installation instructions

## Install Gluu 4.1 software

```
# echo "deb https://repo.gluu.org/ubuntu/ bionic-devel main" > /etc/apt/sources.list.d/gluu-repo.list
# curl https://repo.gluu.org/ubuntu/gluu-apt.key | apt-key add -
# apt update
# apt install gluu-server
# /sbin/gluu-serverd start
# /sbin/gluu-serverd login

```

See [Instructions on installing Gluu Gateway 4.1](https://github.com/GluuFederation/gluu-gateway/wiki/Installation-development-build)
