# Pipes

----

## Running

Run as a module

### Development

#### Widlcard subdomain support

Ngrok for testing

```shell
ngrok tcp 6969
```

Note... only seems to work when ngrok generates 0.something...
Idk why...

#### Run the Webapp

```shell
# Be in /pipes
sanic server:dev --dev --port 6969 --host 0.0.0.0 --single-process
```

using --single-process because otherwise before_server_close
does not trigger...

### Production

Follow `setup-instructions.md` for setting up the server.

#### Run the Webapp

```shell
# Be in /pipes
sanic server:prod --port 6969 --host 0.0.0.0 --single-process
```
