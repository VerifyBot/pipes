# 🚀  Pipes

pipe those webhooks to Discord

## 🎉 Motivation

Many services offer you to add a webhook url to get notified when something happens (eg: [github](https://docs.github.com/en/webhooks/about-webhooks)).

But what if you want a Discord Bot to handle that? <br>
Well, unless you're running on a
server that has a domain / static IP and is reachable from the internet, you're out of luck.

If you're like me, you're going to think about using Discord's Webhook feature to send messages to a channel,
and then intercept those messages with the bot via an [on_message](https://discordpy.readthedocs.io/en/stable/api.html#discord.on_message) event.
Yay, Everything is good now! Right...?

Sadly no, those providers that offer you to add a webhook url don't allow you to customize the payload.
Therefore, while discord requires a payload to be in a specific format, ie: `{"content": "Hello, World!"}`,
the webhook provider might send the payload as `"Hello, World!"`.
Get the problem now?

While solutions like [Pipedream](https://pipedream.com/) or [Zapier](https://zapier.com/) exist (and are so great),
they are not free, or their free tier is very limited (Pipedream allows 25 credits/events per day).

This is where **🚀 Pipes** comes in. It's a simple, self-hosted and free solution to pipe those webhooks to Discord.
All you need is a domain (don't be scared) and a server (DigitalOcean offers a generous free tier).

You may also use the official [**🚀 Pipes**](https://usepipes.web.app/) website (server uptime is not guarenteed)

Hopefuly, this will help you as much as it helped me.

## 🎯 Goals

- [x] In order to avoid/monitor spammers and abuse, I want to implement an authentication system.
        The current solution is Discord's OAuth2, that way I can both verify that you even need this service,
        and if I ever want to add features that require Discord user data, I can change the scope and do so.
- [x] One of my main gols is to be able to have dynamic subdomains, just because it's cool:
    ```
    Your URLs:
    374753f3.m.pipes.me --> https://discord.com/api/webhooks/...
    d64319bb.m.pipes.me --> https://discord.com/api/webhooks/...
    3b231f9d.m.pipes.me --> https://discord.com/api/webhooks/...
    ...
    ```
    
    


## 📦 Installation (W.I.P)

I'll hopefully use Docker for this :)

You need to:
  - setup a server, get a domain.
  - clone the repo
  - build the ui (npm i && npm run build)
  - setup the config.ini under `server`
  - run the server in the background (tmux, etc.)