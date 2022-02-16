import cv2
from ..hand import Hand
from pynput.keyboard import Controller, Key
from time import sleep
import datetime
class Button:
    def __init__(self, pos, text, size=[50, 50]):
        self.pos = pos
        self.size = size
        self.text = text
        self.previous_keyactivate=False



class Display:
    def __init__(self):

        self.kb=Controller()
        self.counter=0



    def Button_display(self,img,buttonList):

        for button in buttonList:

            x, y = button.pos
            w, h = button.size


            cv2.rectangle(img, button.pos, (x + w, y + h), (214, 80, 46 ), cv2.FILLED)
            cv2.putText(img, button.text, (x + 5, y + 32),
                        cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 4)



    def Button_selection(self,img,buttonList,domhand: Hand ,keyactivate,width, height ):


        self.keyactivate=keyactivate

        if domhand:
            for button in buttonList:
                x, y = button.pos
                w, h = button.size





                if (x < domhand.index_tip.x* width < (x + w)) and (y < domhand.index_tip.y* height< (y + h)) :
                    cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (107, 49, 13), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 65),
                                cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)


                    ## when clicked
                    if self.keyactivate is True :


                        self.counter += 1



                        if self.counter == 2 :
                            print(datetime.datetime.now(), "- Keyboard Mode ")
                            print("Keyboard Press Detected:",  button.text)


                            if button.text == "<":
                                self.kb.press(Key.backspace)
                            else:

                                self.kb.press(button.text)
                                cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                                cv2.putText(img, button.text, (x + 20, y + 65),
                                            cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                    else:

                        self.counter=0





