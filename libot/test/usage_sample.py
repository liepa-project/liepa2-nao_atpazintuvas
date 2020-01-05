# -*- coding: utf-8 -*-
import libot.nao_dialog_trainer as nao_dialog_trainer
import libot.nao_dialog_model as nao_dialog_model


def main():


#     dialog_str = """topic: ~test_dialog()
# language: ltu
# u:(Labas) Sveiki
# u:(Kaip tau sekasi) Normoje
# u:(kuri diena) geroji
# u:(e:Dialog/Fallback) Neturiu atsakymo"""

    f = open("./test/topics/game.top", "r")
    # f = open("./test/topics/simple.top", "r")
    dialog_str = f.read()
    f.close()

    naoDialogTrainer = nao_dialog_trainer.NaoDialogTrainer()
    naoDialogModel = naoDialogTrainer.train(dialog_str)
    naoDialogContext = nao_dialog_model.NaoDialogContext()
    naoDialogUtil = nao_dialog_model.NaoDialogUtil()

    chart = naoDialogTrainer.generate_dialog_chart(naoDialogModel)
    print(chart)

    warmup = ["labas",
        "Noriu pradėti žaidimą",
        "ne",
        "ne",
        "taip"]
    for line in warmup:
        naoDialogUtil.find_response(naoDialogModel, naoDialogContext, line)

    while True:
        val = input("💬  > ")
        response=naoDialogUtil.find_response(naoDialogModel, naoDialogContext, val)
        print("🤖\t" + response.responseText)
        if(response.eventValue):
            print("🤖\t\t eventValue: " + response.eventValue)
if __name__ == "__main__":
    main()