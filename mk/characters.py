from configparser import ConfigParser

class MKCharacter:

    def __init__(self):
        self.actions = {}
        self.actions.update(self.char_actions('GENERAL'))

    def char_actions(self, char_name):
        controls = {}
        config = ConfigParser()
        config.read('./config/controls.ini')
        for (cur_key, cur_val) in config.items(char_name):
            controls[cur_key] = cur_val
        return controls        

        
class SonyaCharacter(MKCharacter):

    def __init__(self):
        super().__init__()
        self.actions.update(self.char_actions('SONYA'))