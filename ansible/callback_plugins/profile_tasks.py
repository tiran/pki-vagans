import datetime
import os
import time


class CallbackModule(object):
    """
    A plugin for timing tasks
    """
    def __init__(self):
        self.stats = {}
        self.current = None

    def playbook_on_task_start(self, name, is_conditional):
        """
        Logs the start of each task
        """

        if os.getenv("ANSIBLE_PROFILE_DISABLE") is not None:
            return

        if self.current is not None:
            # Record the running time of the last executed task
            self.stats[self.current] = time.time() - self.stats[self.current]

        # Record the start time of the current task
        self.current = name
        self.stats[self.current] = time.time()

    def playbook_on_stats(self, stats):
        """
        Prints the timings
        """

        if os.getenv("ANSIBLE_PROFILE_DISABLE") is not None:
            return

        # Record the timing of the very last task
        if self.current is not None:
            self.stats[self.current] = time.time() - self.stats[self.current]

        # Sort the tasks by their running time
        results = sorted(
            self.stats.items(),
            key=lambda value: value[1],
            reverse=True,
        )

        # Print the timings
        fast = 0
        fast_threshold = 0.5
        for name, elapsed in results:
            if elapsed < fast_threshold:
                fast += 1
                continue
            print(
                "{0:-<70}{1:->9}".format(
                    '{0} '.format(name),
                    ' {0:.02f}s'.format(elapsed),
                )
            )

        print("{0} tasks faster than {1} seconds".format(fast, fast_threshold))

        total_seconds = sum([x[1] for x in self.stats.items()])
        print("\nPlaybook finished: {0}, {1} total tasks.  {2} elapsed. \n".format(
                time.asctime(),
                len(self.stats.items()),
                datetime.timedelta(seconds=(int(total_seconds)))
                )
          )

    def set_options(self):
        None