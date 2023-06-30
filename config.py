import os

class Config(object):
  API_ID = int(os.environ.get("API_ID", "20862286"))
  API_HASH = os.environ.get("API_HASH", "b069c4c5a46d755502e2a21f278b40ee")
  BOT_TOKEN = os.getenv("BOT_TOKEN", "6195387133:AAFFfYbDM97clW4f99j-b2ObmDKDHJpgj5c")
  STRINGSESSION = os.environ.get("STRINGSESSION", "1BVtsOL8BuzBqHFIKANmPtd11wW7Khk95T7iezbedBKiGXVRLnP6wiCxX8JcAZ7y8gmDHHClF2cXc_UuKO3xikQNZUUvVB7LZVbNt5vYVSf5vVHocqHcIv_nfeflzZIEp-3gegMggYlWVE1LyBUbUh35IU60B32kjswQxLzoDIwzwIu6F_EleWdTmNTitX-D_yxsJ3rKR58ki58Zod84xVcauXLDDxwhU5l3EjvNakLn6-AwO3_QpHxyRzqXlO_ixz6B7NqBfrr3YgmBrjxfJuT3TV_Qsj-eai97hWk99knWMFFJbKt2WMk_8rC535b5UhSDiZaN5v47_NMgtRq1CSuWOs5XSlVU=")
  OWNER_ID = int(os.environ.get("OWNER_ID", "5558463511"))
  DATABASE_CHANNELS = os.environ.get("DATABASE_CHANNELS", ["-1001935504406"])
  DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://xrawexvl:mamtDtntbyOjvQmQv1I7LamiifYVj1T1@tiny.db.elephantsql.com/xrawexvl")
  DELETE_DELAY = int(os.environ.get("DELETE_DELAY", 120))
  SUBSCRIPTION_TIME = int(os.getenv("SUBSCRIPTION_TIME", "31"))
  FORCESUB_CHANNEL = os.getenv("FORCESUB_CHANNEL", -1001932233757)
  OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "owner_21")
  BOT_USERNAME = os.environ.get("BOT_USERNAME", "@Fuck_the_world_bot")
