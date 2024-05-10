from sanic import Request, text, HTTPResponse


async def route_hello(request: Request):
  return text("Hello, World!")


async def route_health(request: Request):
  # just return status code ok. no body
  return HTTPResponse(status=204, content_type='text/plain; charset=utf-8')
