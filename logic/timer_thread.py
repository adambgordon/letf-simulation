import time
import threading
import sys

# Thread that prints the elapsed time
class ElapsedTimeThread(threading.Thread):

    def __init__(self):
        super(ElapsedTimeThread, self).__init__()
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):

        dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        index = 0
        last_half_second = 0

        print()
        thread_start = time.time()

        while not self.stopped():
            duration = time.time()-thread_start

            current_half_second = int(duration/0.1)
            if (current_half_second != last_half_second):
                last_half_second = current_half_second
                index += 1
                if (index == len(dots)):
                    index = 0
            
            print("Aggregating data... {}".format(dots[index]))
            print("{:.2f} seconds\n".format(duration))
            sys.stdout.write("\033[F"*3)

            # Delay to prevent needless over-utilization of CPU
            time.sleep(0.01)

        print("Aggregation complete\033[K")
        print("{:.2f} seconds\033[K\n".format(time.time()-thread_start))
