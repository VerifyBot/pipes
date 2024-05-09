# Pipes

## How to run

Run as a module

```shell
# Be in /pipes
sanic server:app --dev --port 6969 --host 0.0.0.0
```

Ngrok for testing

```shell
ngrok tcp 6969
```
Note... only seems to work when ngrok generates 0.something...
Idk why...