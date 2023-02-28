if [ -d "/URL-Shortener-V2" ]
then
  echo "Deleting existing directory..."
  rm -rf /URL-Shortener-V2
fi

if [ -z $SOURCE_CODE ]
then
  echo "Cloning main Repository"
  git clone https://github.com/kevinnadar22/URL-Shortener-V2.git /URL-Shortener-V2
else
  echo "Cloning Custom Repo from $SOURCE_CODE "
  git clone $SOURCE_CODE /URL-Shortener-V2
fi
cd /URL-Shortener-V2
python3 -m venv venv
source venv/bin/activate
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 -m main
