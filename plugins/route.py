import datetime
from aiohttp import web
from helpers import temp

routes = web.RouteTableDef()


@routes.get("/", allow_head=True)
async def root_route_handler(request):
    runtime = datetime.datetime.now()
    t = runtime - temp.START_TIME
    runtime = str(datetime.timedelta(seconds=t.seconds))

    res = {
        "status": "running",
        "bot": temp.BOT_USERNAME,
        "runtime": runtime,
    }
    return web.json_response(res)
