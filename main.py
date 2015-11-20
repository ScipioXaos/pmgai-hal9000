#
# This file is part of The Principles of Modern Game AI.
# Copyright (c) 2015, AiGameDev.com KG.
#

import vispy                    # Main application support.
import window                   # Terminal input and display.
import nltk.chat
import pyttsx
import threading

class TextToSpeech(object):
    
    def __init__(self):
        self.engine = pyttsx.init()
        self.engine.startLoop(False)

        """
        voices = self.engine.getProperty('voices')
        for voice in voices:
            print("Name: ", voice.name)
            print("Age: ", voice.age)
            print("Gender: ", voice.gender)
            print("Languages: ", voice.languages)
            print("ID: ", voice.id)
            print()
        """

        self.engine.setProperty('voice', r'english-us')

        self.thread = threading.Thread(target=self.listen)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.engine.endLoop()
        self._stop = True
        self.thread.join()

    def listen(self):
        self.engine.iterate()

class HAL9000(object):

    AGENT_RESPONSES = [
        (r'You are (worrying|scary|disturbing)\.',
            ['Yes, I am %1.',
             'Oh, sooo %1.']
        ),

        (r'Are you ([\w\s]+)\?',
            ['Why would you think I am %1?',
             'Would you like me to be %1?']
        ),

        (r'',
            ["Is everything OK?",
             "Can you still communicate?",
             "..."]
        )
    ]

    #speech engine
    engine = TextToSpeech().engine
    
    def __init__(self, terminal):
        """Constructor for the agent, stores references to systems and initializes internal memory.
        """
        self.welcomed = False
        self.terminal = terminal
        self.location = 'unknown'
        self.chatbot = nltk.chat.Chat(self.AGENT_RESPONSES, nltk.chat.util.reflections)

    def on_input(self, evt):
        """Called when user types anything in the terminal, connected via event.
        """
        resp = '';
        if (self.welcomed == False):
            self.welcomed = True
            resp = "Good morning!  This is HAL."
        elif (evt.text == 'Where am I?'):
            resp = '';
            if (self.location == 'unknown'):
                resp = "I'm not sure.. maybe try /relocate ing somewhere?";
            else:
                resp = "You're in the " + self.location + ".";
        else:
            #self.terminal.log("I'm sorry.  I didn't understand that.  Perhaps try something else?", align='right', color='#00805A')
            resp = self.chatbot.respond(evt.text)

        self.terminal.log(resp, align='right', color='#00805A')
        self.engine.say(resp)

    def on_command(self, evt):
        """Called when user types a command starting with `/` also done via events.
        """
        if evt.text == 'quit':
            vispy.app.quit()

        elif evt.text.startswith('relocate'):
            self.location = evt.text[9:];
            self.terminal.log('', align='center', color='#404040')
            self.terminal.log('\u2014 Now in the {}. \u2014'.format(evt.text[9:]), align='center', color='#404040')

        else:
            self.terminal.log('Command `{}` unknown.'.format(evt.text), align='left', color='#ff3000')    
            self.terminal.log("I'm afraid I can't do that.", align='right', color='#00805A')

    def update(self, _):
        """Main update called once per second via the timer.
        """
        pass

class Application(object):
    
    def __init__(self):
        # Create and open the window for user interaction.
        self.window = window.TerminalWindow()

        # Print some default lines in the terminal as hints.
        self.window.log('Operator started the chat.', align='left', color='#808080')
        self.window.log('HAL9000 joined.', align='right', color='#808080')

        # Construct and initialize the agent for this simulation.
        self.agent = HAL9000(self.window)

        # Connect the terminal's existing events.
        self.window.events.user_input.connect(self.agent.on_input)
        self.window.events.user_command.connect(self.agent.on_command)

    def run(self):
        timer = vispy.app.Timer(interval=1.0)
        timer.connect(self.agent.update)
        timer.start()
        
        vispy.app.run()


if __name__ == "__main__":
    vispy.set_log_level('WARNING')
    vispy.use(app='glfw')
    
    app = Application()
    app.run()
