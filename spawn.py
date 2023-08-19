import sys, subprocess, time, random, os
from threading import Thread

class ProcessClient:
    def __init__(self, port, opponents):
        self.port = port
        self.opponents = opponents

    def call(self):
        subprocess.call(['python3', 'monte_client.py', str(self.port), random.choice(self.opponents)])

    @property
    def str_port(self):
        return str(self.port)

def call(port):
    subprocess.call(['python3', 'monte_client.py', str(port)])


def form_saves(base_fname, char_name):
    opponents = ["bro_zero", "cyrax", "ermac", "jade", "jax", "kabal", "kano", "kitana", "kung_lao", "liu_kang", "mileena", "nightwolf", "noob", "og_zero","rain", "reptile", "scorpion", "sektor", "shang_tsung", "sindel", "smoke", "sonya", "stryker"]
    assert(len(opponents) == 23)
    fnames = []
    for opponent in opponents:
        fname = f"{base_fname}/{char_name}/{opponent}.sst"
        if os.path.exists(fname):
            fnames.append(fname)
        else:
            print(f"{fname} does not exist")
    assert(len(fnames) == 23)
    return fnames


if __name__ == '__main__':
    #ports = [51000, 52000, 53000, 54000, 55000, 56000, 57000, 58000, 59000, 51200, 51300, 51400, 51500, 51600, 51700, 51800, 51900, 52100, 52300, 52400, 52500, 52600, 53100, 53200, 53300]
    ports = list(range(52000, 52030))
    fnames = form_saves("/home/dustin/mk_saves/ai", "sonya")
    threads = {}
    for port in ports:
        print(f"STARTING {port}")
        cur_thread = Thread(target=ProcessClient(port, fnames).call)
        cur_thread.start()
        threads[str(port)] = cur_thread


    while True:
        print("CHECKING")
        for thread_port in threads.keys():
            if not threads[thread_port].is_alive():
                new_thread = Thread(target=ProcessClient(int(thread_port), fnames).call)
                new_thread.start()
                threads[thread_port] = new_thread
        time.sleep(10)