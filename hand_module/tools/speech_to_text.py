import speech_recognition as sr
from pynput.keyboard import Controller
from ..gestures.gesture import Gesture
import multiprocessing
from time import sleep

class speechToText():
    def __init__(self, gestures: Gesture):

        # Gesture recognition
        self.detection_gesture = gestures.get_gesture("dbgun", "offhand")
        
        #Activation and deactivation parameters
        self.activated = False
        self.activation_frames = 5
        self.activation_buffer = [0 for _ in range(self.activation_frames)]
        self.prev_mode = False

        # Setting up a new process to run the multiprocessing on
        
        self.queue_manager = multiprocessing.Manager()
        self.status_queue = self.queue_manager.Queue()  # queue to get the 'status' of where in the speech-to-text process is

        self.activation_queue = multiprocessing.Queue()  # queue to detect if speech to text should be active or not
        
        self.listen_in_background = multiprocessing.Process(target = background_process,args = (1,self.activation_queue,self.status_queue)) # create a new process object
        self.listen_in_background.daemon = True # This will allow the background process to be killed if the main process is
        self.listen_in_background.start() # start the new process
        
        self.status = None # Can be None, Recording, Processing, Sucess, Faliure or Error 

    def update_activated(self):
        self.activation_buffer.pop(0)
        if self.detection_gesture.is_active:
            self.activation_buffer.append(1)
        else:
            self.activation_buffer.append(0)
        
        if sum(self.activation_buffer) == self.activation_frames:
            self.activated = True
        else:
            self.activated = False

    def update_status(self):
        if self.status_queue.qsize() > 0:
            self.status = self.status_queue.get()

    def run_speech_recognition(self):
        self.update_activated()
        if self.activated and self.prev_mode == False:
            self.activation_queue.put(1)
        self.prev_mode = self.activated
        self.update_status()

class speechProcessor():
        def __init__(self,status_queue):
            self.r = sr.Recognizer()
            print("Set up the recogniser engine")
            self.mic = sr.Microphone(0)
            print("Connected to the microphone")
            self.speech_engine = "Google"
            self.min_loudness_detection = 500
            self.recognition_timeout = 5
            self.sentence_time_limit = 15
            self.keyboard = Controller()
            self.available_to_run = True
            self.processing = False
            self.status_queue = status_queue

        def set_energy_threshold(self,source):
            self.r.adjust_for_ambient_noise(source,duration = 0.5)
            if self.r.energy_threshold < self.min_loudness_detection:
                self.r.energy_threshold = self.min_loudness_detection

        def type_text(self,text: str):
            if text and text != "":
                self.keyboard.type(text)
            

        def clear_queue(self):
            if self.status_queue.qsize() > 0:
                self.status_queue.get()
        
        def recognise(self):
            with self.mic as source:
                text = None
                self.set_energy_threshold(source)
                print("Ok, ready to go, start speaking")
                try:
                    self.clear_queue()
                    self.status_queue.put("Recording")
                    audio = self.r.listen(source,self.recognition_timeout,self.sentence_time_limit)
                    print("sucessfully finished listening")
                    if self.speech_engine == "Google":
                        print("Thankyou. Sending data up to Google....\n")
                        self.clear_queue()
                        self.status_queue.put("Processing")
                        text = self.r.recognize_google(audio)
                        self.clear_queue()
                        self.status_queue.put("Sucess")
                        print("You said: " + text + "\n")
                except sr.RequestError:
                    errstring = "Sorry, you need to connect to the internet for this to work"
                    self.clear_queue()
                    self.status_queue.put(errstring)
                    print(errstring)
                    sleep(3)
                except sr.WaitTimeoutError:
                    errstring = "Sorry, you took too long to speak"
                    self.clear_queue()
                    self.status_queue.put(errstring)
                    print(errstring)
                    sleep(3)
                except sr.UnknownValueError:
                    errstring = "Sorry, could not understand you"
                    self.clear_queue()
                    self.status_queue.put(errstring)
                    print(errstring)
                    sleep(3)
                except Exception:
                    errstring = "Sorry something went wrong"
                    self.clear_queue()
                    self.status_queue.put(errstring)
                    print(errstring)
                    sleep(3)
            return text

        def run_speech_recognition(self):
            if self.mic is not None:
                self.available_to_run = False
                self.clear_queue()
                self.status_queue.put("Ready")
                text = self.recognise()
                self.type_text(text)
                self.available_to_run = True
                self.clear_queue()
                self.status_queue.put("Finished")
            else:
                print("cannot find mic")


def background_process(num,activation_queue,status_queue):
    if 's' not in locals():
        s = speechProcessor(status_queue)

    while True:
        if not activation_queue.empty():
            if 's' in locals() and s.available_to_run:
                s.run_speech_recognition()
            activation_queue.get()