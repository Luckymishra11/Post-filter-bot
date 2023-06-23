if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone $ORIGINAL_REPO /Filter-Bot
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /Filter-Bot
fi
cd /Filter-Bot
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 bot.py