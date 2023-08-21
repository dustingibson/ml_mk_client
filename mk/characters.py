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

    def gen_indexes(self) -> dict[str,int]:
        return {
            "roundhouse": 0,
            "sweep": 1,
            "throw": 2,
            "uppercut": 3,
            "lowkick": 4,
            "highkick": 5,
            "highpunch": 6,
            "lowpunch": 7,
            "forward": 8,
            "back": 9,
            "up": 10,
            "down": 11,
            "block": 12
        }        

        
class SonyaCharacter(MKCharacter):

    def __init__(self):
        super().__init__()
        self.actions.update(self.char_actions('SONYA'))

    def gen_indexes(self) -> dict[str,int]:
        out_dict = super().gen_indexes()
        out_dict.update({
            "ringtoss": 13,
            "leggrab": 14,
            "squarewave": 15,
            "bicyclekick": 16 
        })
        return out_dict