import threading
import time
import random
from enum import Enum

class State(Enum):
    THINKING = "đang suy nghĩ"
    HUNGRY = "đang đói"
    EATING = "đang ăn"

class Chopstick:
    def __init__(self, id):
        self.id = id
        self.lock = threading.Semaphore(1)

    def pick(self):
        self.lock.acquire()

    def drop(self):
        self.lock.release()

class Philosopher:
    def __init__(self, id, left, right, sim):
        self.id = id
        self.left = left
        self.right = right
        self.sim = sim
        self.state = State.THINKING
        self.held = []

    def update(self, state, held=None):
        self.sim.display_lock.acquire()
        self.state = state
        if held is not None:
            self.held = held
        self.sim.display_lock.release()

    def think(self):
        self.update(State.THINKING, [])
        # time.sleep(random.uniform(0.001, 0.005))

    def eat(self):
        self.update(State.EATING, [self.left.id, self.right.id])
        # time.sleep(0.009)

    def run(self):
        while True:
            self.think()
            self.update(State.HUNGRY, [])

            # Bỏ xử lý deadlock: Không sắp xếp đũa theo thứ tự ID nữa
            # Mỗi triết học gia luôn lấy đũa trái trước, sau đó lấy đũa phải

            # Lấy đũa bên trái
            self.left.pick()
            self.update(State.HUNGRY, [self.left.id])

            # Lấy đũa bên phải
            self.right.pick()

            # Ăn
            self.eat()

            # Thả đũa
            self.right.drop()
            self.left.drop()

class PhilosopherSim:
    def __init__(self, count=5, duration=10, log_file="philosopher_sim.log"):
        self.count = count
        self.duration = duration
        self.display_lock = threading.Semaphore(1)
        self.log_file = log_file
        self.start_time = 0

        self.init_log_file()

        self.sticks = [Chopstick(i) for i in range(count)]

        self.philosophers = []
        for i in range(count):
            left = self.sticks[i]
            right = self.sticks[(i + 1) % count]
            self.philosophers.append(Philosopher(i, left, right, self))
        self.display_thread = None

    def init_log_file(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("MÔ PHỎNG BÀI TOÁN NHỮNG TRIẾT HỌC GIA ĂN TỐI\n")
            f.write("=" * 70 + "\n\n")

    def log_status(self, status_text):
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(status_text + "\n")

    def show_status(self):
        self.display_lock.acquire()
        try:
            elapsed = time.time() - self.start_time
            status_text = f"\nTrạng thái tại thời điểm {elapsed:.3f}s:"
            status_text += "\n" + "=" * 70

            for phil in self.philosophers:
                sticks_info = f"đũa {', '.join(map(str, phil.held))}" if phil.held else "không có đũa"
                phil_status = f"\nTriết học gia {phil.id}: {phil.state.value}, {sticks_info}"
                status_text += phil_status

            status_text += "\n" + "=" * 70

            print(status_text)
            self.log_status(status_text)
        finally:
            self.display_lock.release()

    def display_loop(self):
        while True:
            self.show_status()
            time.sleep(0.005)

    def start(self):
        self.start_time = time.time()

        self.display_lock.acquire()
        start_message = f"Bắt đầu mô phỏng với {self.count} triết học gia vào {time.strftime('%Y-%m-%d %H:%M:%S')}"
        print(start_message)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(start_message + "\n\n")
        self.display_lock.release()

        self.display_thread = threading.Thread(target=self.display_loop, daemon=True)
        self.display_thread.start()

        for phil in self.philosophers:
            threading.Thread(target=phil.run, daemon=True).start()

        try:
            time.sleep(self.duration)

            self.display_lock.acquire()
            end_message = f"\nKết thúc mô phỏng sau {self.duration} giây"
            print(end_message)
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(end_message + "\n")
                f.write(f"Thời gian kết thúc: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.display_lock.release()

        except KeyboardInterrupt:
            self.display_lock.acquire()
            interrupt_message = "\nMô phỏng đã bị dừng bởi người dùng"
            print(interrupt_message)
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(interrupt_message + "\n")
            self.display_lock.release()

if __name__ == "__main__":
    PhilosopherSim(count=5, duration=5).start()