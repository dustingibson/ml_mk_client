import sys, subprocess, time
from threading import Thread

class ProcessClient:
    def __init__(self, port):
        self.port = port

    def call(self):
        subprocess.call(['python3', 'monte_client.py', str(self.port)])

    @property
    def str_port(self):
        return str(self.port)

def call(port):
    subprocess.call(['python3', 'monte_client.py', str(port)])


if __name__ == '__main__':
    ports = [51000, 52000, 53000, 54000, 55000, 56000, 57000, 58000, 59000, 51200, 51300, 51400, 51500, 51600, 51700, 51800, 51900, 52100, 52300, 52400, 52500, 52600, 53100, 53200, 53300]
    threads = {}
    for port in ports:
        print(f"STARTING {port}")
        cur_thread = Thread(target=ProcessClient(port).call)
        cur_thread.start()
        threads[str(port)] = cur_thread


    while True:
        print("CHECKING")
        for thread_port in threads.keys():
            if not threads[thread_port].is_alive():
                new_thread = Thread(target=ProcessClient(int(thread_port)).call)
                new_thread.start()
                threads[thread_port] = new_thread
        time.sleep(10)