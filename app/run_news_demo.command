#! /bin/bash
cd ~/venv/bin
source activate
cd ~/projects/news/app
python routes.py

# run the following command in terminal first to give the terminal permission to run this file
# chmod u+x ~/projects/news/app/run_news_demo.command

# url for this app is http://127.0.0.1:5000/