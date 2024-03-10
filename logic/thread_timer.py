import time
import threading
import sys

# Thread that prints the elapsed time
class ElapsedTimeThread(threading.Thread):

    def __init__(self):
        super().__init__()
        self.stop_event = threading.Event()
        self.dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def stop(self):
        self.stop_event.set()

    def stopped(self):
        return self.stop_event.is_set()

    def run(self):

        print()
        index = 0
        start_time = time.time()

        while not self.stopped():
            duration = time.time() - start_time
            index = int(duration / 0.1) % len(self.dots)
            
            print(f"Aggregating data... {self.dots[index]}")
            print(f"{duration:.2f} seconds\n")
            sys.stdout.write("\033[F"*3)

            # Delay to prevent needless over-utilization of CPU
            time.sleep(0.01)

        print("Aggregation complete\033[K")
        print(f"{time.time() - start_time:.2f} seconds\033[K\n")
