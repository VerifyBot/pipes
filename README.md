# 🚀  Pipes

pipe those webhooks to Discord

## 🎉 Motivation

Many services offer you to add a webhook url to get notified when something happens.

But what if you want a Discord Bot to handle that? <br>
Well, unless you're running on a
server that has a domain / static IP and is reachable from the internet, you're out of luck.

If you're like me, you're going to think about using Discord's Webhook feature to send messages to a channel,
and then intercept those messages with the bot via an [on_message](https://discordpy.readthedocs.io/en/stable/api.html#discord.on_message) event.
Yay, Everything is good now! Right...?

Sadly no, those providers that offer you to add a webhook url, they don't allow you to customize the payload.
Therefore, while discord requires a payload to be in a specific format, ie: `{"content": "Hello, World!"}`,
the webhook provider might send the payload as `"Hello, World!"`.
Get the problem now?

While solutions like [Pipedream](https://pipedream.com/) or [Zapier](https://zapier.com/) exist (and are so great),
they are not free, or their free tier is very limited (Pipedream allows 100 events per day).

This is where **Pipes** comes in. It's a simple, self-hosted and free solution to pipe those webhooks to Discord.
All you need is a domain (don't be scared) and a server (DigitalOcean offers a generous free tier).

Hopefuly, this will help you as much as it helped me.

## 🎯 Goals
My goal is to be able to have dynamic subdomains, just because it's cool:
```
Your URLs:
374753f3.m.pipes.me --> https://discord.com/api/webhooks/...
d64319bb.m.pipes.me --> https://discord.com/api/webhooks/...
3b231f9d.m.pipes.me --> https://discord.com/api/webhooks/...
...
```

I've done it one time with PHP like 4 years ago (.htaccess).

Future reference for me: [Let's Encrypt FAQ](https://letsencrypt.org/docs/faq/#does-let-s-encrypt-issue-wildcard-certificates), [DigitalOcean Tutorial](https://www.digitalocean.com/community/tutorials/how-to-create-let-s-encrypt-wildcard-certificates-with-certbot).

In case I won't manage (or it's too expensive), I'll just use a single domain, and have it like:
`m.pipes.me/374753f3`, etc. Which is still cool, but not as cool as the first one :).



## 📦 Installation (W.I.P)

I'll hopefully use Docker for this :)

You need to:
  - setup a server, get a domain.
  - clone the repo
  - build the ui (npm i && npm run build)
  - setup the config.ini under `server`
  - run the server in the background (tmux, etc.)