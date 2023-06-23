import os

class Config(object):
  API_ID = int(os.environ.get("API_ID", "8321183"))
  API_HASH = os.environ.get("API_HASH", "d9102799310e7038de04d9af2679ed68")
  BOT_TOKEN = os.getenv("BOT_TOKEN", "6124714988:AAHf0FZOHmagJ5W_XU5sIgvsgrPxBGqVHFo")
  STRINGSESSION = os.environ.get("STRINGSESSION", "1BVtsOHcBu5sUSNrqSFZ8v_GNQRTP1t6MV4qaSW2slMBC8wgr7CGJLbE9weLEnSXVp6Dm2VUfE9OZSyhs6ScRDzo4XVkpWjz0YXMPEFKTpSNshB7s7szPkuCmb3QeIjUTc-0eulxOEk__DVcaGC4zsYXY1O1XPz2A2VIKNvffaPSeJh3KqKFl6noevVkItuBCiIswdxJH0q-zVo1BXiEVz_Md0OnGODJcT9Ot0V8QdgTQ-mBwv0X4e-KSkmK0dO2qVgXoHXzb84tlU1Cs_MAhzKuBvM9fXnsReCI3jmNPkbiYQe1ZR8aFOzI_iA_O3-41u_9itDOHY--6bmoBSYOGENRPbr7lmnY=")
  OWNER_ID = int(os.environ.get("OWNER_ID", "5651594253"))
  DATABASE_CHANNELS = os.environ.get("DATABASE_CHANNELS", ["-1001932233757"])
  DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://kxygsjfk:KO8VSr9tAOXjo3rbmu8wMG9pBcN3veZb@babar.db.elephantsql.com/kxygsjfk")
  DELETE_DELAY = int(os.environ.get("DELETE_DELAY", 120))
  SUBSCRIPTION_TIME = int(os.getenv("SUBSCRIPTION_TIME", "31"))
  FORCESUB_CHANNEL = os.getenv("FORCESUB_CHANNEL", -1001932233757)
  OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "J_shree_ram")
  BOT_USERNAME = os.environ.get("BOT_USERNAME", "Postfinder_bot")
