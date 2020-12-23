# oversimplified_pybot
Dialog managment chat bot, without bells and whistles.


curl -XPOST http://localhost:8000  -F 'message=Labas'


Train chat:
python3 -m oversimbot_train.parser.chat_trainer

Run engine:
python -m unittest test/nao_dialog_test.py
python2 -m unittest test.nao_dialog_test
python2 -m unittest test.nao_dialog_test.NaoDialogTest.test_dialog_generate_resouces

# Docker

docker build -t oversimbot_engine .

docker run -it -p 8000:8000 oversimbot_engine

docker run -it oversimbot_engine /bin/bash
