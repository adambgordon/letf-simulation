import time
import threading
import sys

class ElapsedTimeThread(threading.Thread):
    """A class to represent a thread that prints the elapsed time."""

    def __init__(self):
        """Initialize the thread and prepare the stop event."""
        super().__init__()
        self.stop_event = threading.Event()
        # Dots used for the progress indicator
        self.dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def stop(self):
        """Stop the thread by setting the stop event."""
        self.stop_event.set()

    def stopped(self):
        """Check if the thread has been stopped."""
        return self.stop_event.is_set()

    def run(self):
        """Run the thread, printing the elapsed time and a progress indicator."""
        print()
        index = 0
        start_time = time.time()

        # Keep running until the thread is stopped
        while not self.stopped():
            duration = time.time() - start_time
            # Update the progress indicator based on the elapsed time
            index = int(duration / 0.1) % len(self.dots)
            
            print(f"Aggregating data... {self.dots[index]}")
            print(f"{duration:.2f} seconds\n")
            # Move the cursor up to overwrite the previous progress indicator
            sys.stdout.write("\033[F"*3)

            # Delay to prevent needless over-utilization of CPU
            time.sleep(0.01)

        # Print a completion message and the total elapsed time
        print("Aggregation complete\033[K")
        print(f"{time.time() - start_time:.2f} seconds\033[K\n")
