# Alpine Base image (ABI)
Alpine Base image (ABI) is [alpinelinux](https://alpinelinux.org) minirootfs 
with some [modifications](#Modifications) and latest updates applied.

The idea is to simulate rolling release distro (like Gentoo,Archlinux or Manjaro) behaivor.

It has: 
* latest updates
* non-root application user

## Motivation
Security. 

The purpose of this image is base image with 0 vulnerabilities.

Normally, even base images like `ubuntu` or RedHat's `ubi` contain tons of rarely needed stuff, 
which is hardly needed for your application to run and brings additional vulnerabilities.   


## Editions
### Edge edition
This is standard [alpinelinux](https://alpinelinux.org) image 
with [edge repository](https://wiki.alpinelinux.org/wiki/Edge) enabled.

### Runtime edition (broken)
Contains only minimalistic linux runtime needed to run your application.

Technically this is `edge` edition, but without package manager (apk) and shell (busybox). 
It is replaced by `/bin/true` binary.

Since it has no shell, container cannot be accessed using standard approaches like `docker exec`.
This make runtime secure, but debug and similar stuff is no longer possible. 

## Modifications
ABI contains non-root application user and group(`appuser:appgroup`). 
So you can just add this single line to your `Dockerfile`
```dockerfile
USER appuser
```

### Creating new user
* For `edge` edition it is fairly easy. Just run standard commands:
```dockerfile
RUN addgroup mygroup && adduser myuser mygroup
```
* For `runtime` edition you have to copy you own `/etc/passwd` and `/etc/group` files.
```dockerfile
FROM hadou.io/base/abi:edge as build
RUN addgroup mygroup && adduser myuser mygroup

FROM hadou.io/base/abi:runtime as final
COPY --from=build /etc/passwd /etc/passwd
COPY --from=build /etc/group /etc/group
```

### IP Forwarding disabled
By default, IP Forwarding in ABI is disabled. Normally, container is end user system, and it has single network. 

Also, this modification attempts to fix [CVE-1999-0511](https://github.com/alpinelinux/docker-alpine/issues/278).

Forwarding can be easily enabled by running
```dockerfile
RUN echo "net.ipv4.ip_forward=1" > /etc/sysctl.conf
```

### Custom Repo
ABI uses `alpine.kyberorg.fi` mirror instead of default one. This is fast mirror from Suomi/Finland.

To revert to default repo please use:
```dockerfile
RUN sed -i 's/alpine.kyberorg.fi/dl-cdn.alpinelinux.org\/alpine/g' /etc/apk/repositories
```