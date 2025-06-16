import time
from collections import deque

# IMPORTANT: WE NEED TO MAKE THIS WEIGHTED SINCE NOT EVERY OPERATION MAKES THE SAME NUMBER OF CALLS/SCRAPES
# either that or we need each individual scrape to call this

# The purpose of this class is to limit the rate at which we make calls to APIs so that we don't get throttled
class RateLimitedExecutor:
    max_calls_per_period: int
    period: float
    call_times: deque

    def __init__(self, max_calls_per_period, period):
        self.max_calls_per_period = max_calls_per_period # Fractional not supported
        self.period = period # In seconds
        self.call_times = deque()

    def _apply_rate_limit(self):
        now = time.monotonic()

        # Remove older timestamps from the deque
        while self.call_times and now - self.call_times[0] > self.period:
            self.call_times.popleft()

        # If we have made max calls in this period, just wait
        if len(self.call_times) >= self.max_calls_per_period:
            wait_time = self.period - (now - self.call_times[0])
            time.sleep(wait_time)

        self.call_times.append(now)

    # Calls the function using the rate limiter
    def call(self, func, *args, **kwargs):
        self._apply_rate_limit()
        return func(*args, **kwargs)