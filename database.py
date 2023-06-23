import contextlib
import os
import threading
from sqlalchemy import create_engine
from sqlalchemy import Column, TEXT, Numeric, Boolean, BIGINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import ast
import traceback
from config import Config

DB_URI = Config.DATABASE_URL.replace('postgres://', 'postgresql://')
SUBSCRIPTION_TIME = Config.SUBSCRIPTION_TIME * 86400

engine = create_engine(DB_URI, client_encoding="utf8")
def start() -> scoped_session:
  global engine
  BASE.metadata.bind = engine
  BASE.metadata.create_all(engine)
  return scoped_session(sessionmaker(bind=engine, autoflush=False))


BASE = declarative_base()
SESSION = start()

INSERTION_LOCK = threading.RLock()


class AuthenticatedUsers(BASE):
  __tablename__ = "AuthUsers"
  userid = Column(BIGINT, primary_key=True)
  username = Column(TEXT)
  authenticated = Column(Boolean, default=False)
  time_of_issue = Column(BIGINT, default=0)
  chats = Column(TEXT, default="[]")

  def __init__(self, userid, authenticated, time_of_issue, username, chats):
    self.userid = userid
    self.username = username
    self.authenticated = authenticated
    self.time_of_issue = time_of_issue
    self.chats = chats


class Chats(BASE):
  __tablename__ = "Chats"
  chatid = Column(BIGINT, primary_key=True)
  user = Column(BIGINT, default=0)
  authenticated = Column(Boolean, default=False)
  ConnectedChannels = Column(TEXT, default='[]')
  forcesubchannel = Column(BIGINT, default=0)

  def __init__(self, chatid, authenticated, user, ConnectedChannels,
               forcesubchannel):
    self.chatid = chatid
    self.authenticated = authenticated
    self.user = user
    self.ConnectedChannels = ConnectedChannels
    self.forcesubchannel = forcesubchannel


class Channels(BASE):
  __tablename__ = "Channels"
  channelid = Column(BIGINT, primary_key=True)
  chatid = Column(BIGINT)

  def __init__(self, channelid, chatid):
    self.channelid = channelid
    self.chatid = chatid


class Controls(BASE):
  __tablename__ = "Controls"
  code = Column(TEXT, primary_key=True)
  filter = Column(Boolean)
  autodelete = Column(Boolean)
  grpfilter = Column(Boolean)

  def __init__(self, code, filter, autodelete, grpfilter):
    self.code = code
    self.filter = filter
    self.autodelete = autodelete
    self.grpfilter = grpfilter


AuthenticatedUsers.__table__.create(checkfirst=True, bind=engine)
Chats.__table__.create(checkfirst=True, bind=engine)
Channels.__table__.create(checkfirst=True, bind=engine)
Controls.__table__.create(checkfirst=True, bind=engine)

def is_autodelete():
  try:
    with INSERTION_LOCK:
      code = "global"
      if query := SESSION.query(Controls).get(code):
        return query.autodelete
      query = Controls(code, filter=False, autodelete=False, grpfilter=False)
      SESSION.add(query)
      SESSION.commit()
      return False
  finally:
    SESSION.close()


def allow_autodelete():
  try:
    with INSERTION_LOCK:
      code = "global"
      query = SESSION.query(Controls).get(code)
      if not query:
        query = Controls(code, filter=False, autodelete=True, grpfilter=False)
      query.autodelete = True
      SESSION.add(query)
      SESSION.commit()
      return True
  finally:
    SESSION.close()


def disable_autodelete():
  try:
    with INSERTION_LOCK:
      code = "global"
      query = SESSION.query(Controls).get(code)
      if not query:
        query = Controls(code, filter=False, autodelete=False, grpfilter=False)
      query.autodelete = False
      SESSION.add(query)
      SESSION.commit()
      return True
  finally:
    SESSION.close()


def is_grpfilter():
  try:
    with INSERTION_LOCK:
      code = "global"
      if query := SESSION.query(Controls).get(code):
        return query.grpfilter
      query = Controls(code, filter=False, autodelete=False, grpfilter=False)
      SESSION.add(query)
      SESSION.commit()
      return False
  finally:
    SESSION.close()


def allow_grpfilter():
  try:
    with INSERTION_LOCK:
      code = "global"
      query = SESSION.query(Controls).get(code)
      if not query:
        query = Controls(code, filter=False, autodelete=False, grpfilter=True)
      query.grpfilter = True
      SESSION.add(query)
      SESSION.commit()
      return True
  finally:
    SESSION.close()


def disable_grpfilter():
  try:
    with INSERTION_LOCK:
      code = "global"
      query = SESSION.query(Controls).get(code)
      if not query:
        query = Controls(code, filter=False, autodelete=False, grpfilter=False)
      query.grpfilter = False
      SESSION.add(query)
      SESSION.commit()
      return True
  finally:
    SESSION.close()


def is_filter_pm():
  try:
    with INSERTION_LOCK:
      code = "global"
      if query := SESSION.query(Controls).get(code):
        return query.filter
      query = Controls(code, False, False, False)
      SESSION.add(query)
      SESSION.commit()
      return False
  finally:
    SESSION.close()


def allow_filter_pm():
  try:
    with INSERTION_LOCK:
      code = "global"
      query = SESSION.query(Controls).get(code)
      if not query:
        query = Controls(code, filter=True, autodelete=False, grpfilter=False)
      query.filter = True
      SESSION.add(query)
      SESSION.commit()
      return True
  finally:
    SESSION.close()


def disable_filter_pm():
  try:
    with INSERTION_LOCK:
      code = "global"
      query = SESSION.query(Controls).get(code)
      if not query:
        query = Controls(code, filter=False, autodelete=False, grpfilter=False)
      query.filter = False
      SESSION.add(query)
      SESSION.commit()
      return True
  finally:
    SESSION.close()


def add_chat(chatid):
  try:
    with INSERTION_LOCK:
      chat = SESSION.query(Chats).get(chatid)
      if not chat:
        chat = Chats(chatid=chatid,
                     authenticated=False,
                     user=0,
                     ConnectedChannels='[]',
                     forcesubchannel=0)
      SESSION.add(chat)
      SESSION.commit()
  finally:
    SESSION.close()


def connect_channel(chatid, channelid):
  try:
    with INSERTION_LOCK:
      chat = SESSION.query(Chats).get(chatid)
      channel = SESSION.query(Channels).get(channelid)
      if not chat:
        # chat = Chats(chatid=chatid, ConnectedChannels=f'[{channelid}]')
        return False
      channels = ast.literal_eval(chat.ConnectedChannels)
      channels.append(channelid)
      channels = str(channels)
      chat.ConnectedChannels = channels
      if not channel:
        channel = Channels(channelid=channelid, chatid=chatid)
      # SESSION.add(chat)
      SESSION.add(channel)
      SESSION.commit()
  finally:
    SESSION.close()


def disconnect_channel(chatid, channelid):
  try:
    with INSERTION_LOCK:
      chat = SESSION.query(Chats).get(chatid)
      channel = SESSION.query(Channels).get(channelid)
      return (_extracted_from_disconnect_channel_9(chat, channelid, channel)
              if chat else False)
  finally:
    SESSION.close()


# TODO Rename this here and in `disconnect_channel`
def _extracted_from_disconnect_channel_9(chat, channelid, channel):
  channels = ast.literal_eval(chat.ConnectedChannels)
  try:
    channels.remove(int(channelid))
  except ValueError:
    print(traceback.format_exc())
    return
  channels = str(channels)
  chat.ConnectedChannels = channels
  SESSION.delete(channel)
  SESSION.commit()
  return True


def add_user(userid, username):
  try:
    with INSERTION_LOCK:
      user = SESSION.query(AuthenticatedUsers).get(userid)
      if not user:
        user = AuthenticatedUsers(userid=userid,
                                  username=username,
                                  authenticated=False,
                                  time_of_issue=0,
                                  chats='[]')
      elif username != user.username:
        user.username = username
      SESSION.add(user)
      SESSION.commit()
  finally:
    SESSION.close()


def is_authenticated(userid):
  try:
    with INSERTION_LOCK:
      user = SESSION.query(AuthenticatedUsers).get(userid)
      return user.authenticated if user else False
  finally:
    SESSION.close()


def is_valid(userid, time):
  try:
    with INSERTION_LOCK:
      print('validating user')
      if user := SESSION.query(AuthenticatedUsers).get(userid):
        if user.authenticated:
          calculate = round(time - float(user.time_of_issue))
          if calculate <= SUBSCRIPTION_TIME:
            print('user is valid')
            return True
          else:
            print('not valid')
            unauthenticate_user(userid)
            return False
        else:
          print('not authenticated')
          return False
      else:
        print('user doesnt exist')
        return False
  finally:
    SESSION.close()


def get_validity(userid):
  try:
    with INSERTION_LOCK:
      user = SESSION.query(AuthenticatedUsers).get(userid)
      return float(user.time_of_issue) if user else False
  finally:
    SESSION.close()


def authenticate_user(userid, time):
  try:
    with INSERTION_LOCK:
      user = SESSION.query(AuthenticatedUsers).get(userid)
      user.authenticated = True
      user.time_of_issue = time
      SESSION.commit()
  finally:
    SESSION.close()


def unauthenticate_user(userid):
  try:
    with INSERTION_LOCK:
      user = SESSION.query(AuthenticatedUsers).get(userid)
      user.authenticated = False
      user.time_of_issue = 0
      chats = ast.literal_eval(user.chats)
      for chat in chats:
        unauth_group(chat)
      user.chats = '[]'
      SESSION.commit()
      return True
  finally:
    SESSION.close()


def username_to_id(username):
  try:
    user = SESSION.query(AuthenticatedUsers).filter(
      AuthenticatedUsers.username == username).first()
    return user.userid if user else False
  finally:
    SESSION.close()


def id_to_username(id):
  try:
    user = SESSION.query(AuthenticatedUsers).get(id)
    return user.username if user else 'UnsupportedUser64Bot'
  finally:
    SESSION.close()


def get_chats():
  try:
    with INSERTION_LOCK:
      query = SESSION.query(Chats.chatid).filter(Chats.ConnectedChannels != "[]")
      return [row[0] for row in query]
  finally:
    SESSION.close()


def get_users():
  try:
    with INSERTION_LOCK:
      query = SESSION.query(AuthenticatedUsers.userid).all()
      return [row[0] for row in query]
  finally:
    SESSION.close()


def get_all_chats():
  try:
    with INSERTION_LOCK:
      query = SESSION.query(Chats.chatid).all()
      return [row[0] for row in query]
  finally:
    SESSION.close()


def get_cha():
  try:
    with INSERTION_LOCK:
      query = SESSION.query(Channels.channelid).all()
      return [row[0] for row in query]
  finally:
    SESSION.close()


def get_auth_users():
  try:
    with INSERTION_LOCK:
      query = SESSION.query(AuthenticatedUsers.userid).filter(
        AuthenticatedUsers.authenticated == True)
      return [row[0] for row in query]
  finally:
    SESSION.close()


def get_channels(chatid):
  try:
    with INSERTION_LOCK:
      query = SESSION.query(Chats).get(chatid)
      if not query:
        return False
      channels = query.ConnectedChannels
      channels = ast.literal_eval(channels)
      return False if len(channels) == 0 else channels
  finally:
    SESSION.close()


def get_all_channels():
  try:
    with INSERTION_LOCK:
      query = SESSION.query(Chats.ConnectedChannels).all()
      return [row[0] for row in query] if query else False
  finally:
    SESSION.close()


def is_grp_auth(chatid):
  try:
    with INSERTION_LOCK:
      chat = SESSION.query(Chats).get(chatid)
      return chat.authenticated if chat else False
  finally:
    SESSION.close()


def auth_group(userid, chatid):
  try:
    with INSERTION_LOCK:
      chat = SESSION.query(Chats).get(chatid)
      user = SESSION.query(AuthenticatedUsers).get(userid)
      if not chat:
        return 'no'
      if not user:
        return 'no'
      chats = ast.literal_eval(user.chats)
      if chatid in chats:
        return 'already'
      chats.append(chatid)
      chats = str(chats)
      chat.authenticated = True
      chat.user = userid
      user.chats = chats
      SESSION.commit()
      return True
  finally:
    SESSION.close()


def get_user_chats(userid):
  try:
    with INSERTION_LOCK:
      user = SESSION.query(AuthenticatedUsers).get(userid)
      if not user:
        return False
      chats = ast.literal_eval(user.chats)
      return chats
  finally:
    SESSION.close()


def unauth_group(chatid):
  try:
    with INSERTION_LOCK:
      chat = SESSION.query(Chats).get(
          chatid if str(chatid).startswith('-100') else -chatid)
      channels = (SESSION.query(Channels).filter(Channels.chatid == (
          chatid if str(chatid).startswith('-100') else -chatid)).all())
      if not chat:
        return False
      if channels:
        for channel in channels:
          SESSION.delete(channel)
      user = SESSION.query(AuthenticatedUsers).get(chat.user)
      chat.authenticated = False
      chat.user = 0
      chat.forcesubchannel = 0
      chats = ast.literal_eval(user.chats)
      with contextlib.suppress(Exception):
        chats.remove(chatid)
      chats = str(chats)
      chat.ConnectedChannels = '[]'
      user.chats = chats
      SESSION.commit()
      return True
  finally:
    SESSION.close()


def enable_force_sub(chatid, channelid):
  try:
    with INSERTION_LOCK:
      chat = SESSION.query(Chats).get(chatid)
      if not chat:
        return False
      chat.forcesubchannel = channelid
      SESSION.commit()
      return True
  finally:
    SESSION.close()


def disable_force_sub(chatid):
  try:
    with INSERTION_LOCK:
      chat = SESSION.query(Chats).get(chatid)
      if not chat:
        return False
      chat.forcesubchannel = 0
      SESSION.commit()
      return True
  finally:
    SESSION.close()


def is_force_sub(chatid):
  try:
    with INSERTION_LOCK:
      if chat := SESSION.query(Chats).get(chatid):
        return False if chat.forcesubchannel == 0 else chat.forcesubchannel
      else:
        return False
  finally:
    SESSION.close()
