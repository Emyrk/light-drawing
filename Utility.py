import time

def get_elapsed_time(start_time, end_time=None):
    if start_time is None:
        print("ERROR: Must have a start_time.")
        return

    if end_time is None:
        end_time = time.time()

    return end_time - start_time
