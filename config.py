import os

class Config(object):
  API_ID = int(os.environ.get("API_ID", "20862286"))
  API_HASH = os.environ.get("API_HASH", "b069c4c5a46d755502e2a21f278b40ee")
  BOT_TOKEN = os.getenv("BOT_TOKEN", "6195387133:AAFFfYbDM97clW4f99j-b2ObmDKDHJpgj5c")
  STRINGSESSION = os.environ.get("STRINGSESSION", "1BVtsOL0BuwXpZAJ7_XnMxiF3fF3RHQTjrfZSlaqpZ-BB2HGNfCpm1wWwTz9-7iZbgTblELfDRYdmXA8Rb5g6k729CgVuK3u5gJzlco3G1zR27SAIHkPFVmB4OtOPmYBioQ9scEoCoPO8sHi123vZOfsuJSToh3kGFE9e3l8gKolLyWKxSqj5yx7umELPFLFoauAY8icQqEGWS0WKDGc-fip55--zGYl_YoDqOjropiKm5-Y3KRsjEGTJBD7wWyasz60SfZFaUAxH4NU-pFvTK1G_SajEpklsSzb1eLbR9DqmblXHR3ezNGYiajr3e0eApYViN2BRiTDzSgz6N4-czvTM7-C69k8=")
  OWNER_ID = int(os.environ.get("OWNER_ID", "5558463511"))
  DATABASE_CHANNELS = os.environ.get("DATABASE_CHANNELS", ["-1001935504406"])
  DATABASE_URL = os.environ.get("DATABASE_URL", "mongodb+srv://mishrajaynishra:f3ewLPvuPeq0M1sB@cluster0.raknipt.mongodb.net/?retryWrites=true&w=majority")
  DELETE_DELAY = int(os.environ.get("DELETE_DELAY", 120))
  SUBSCRIPTION_TIME = int(os.getenv("SUBSCRIPTION_TIME", "31"))
  FORCESUB_CHANNEL = os.getenv("FORCESUB_CHANNEL", -1001932233757)
  OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "owner_21")
  BOT_USERNAME = os.environ.get("BOT_USERNAME", "@Fuck_the_world_bot")
