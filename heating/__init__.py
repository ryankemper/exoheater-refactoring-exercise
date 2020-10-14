import datetime
import socket
import requests

# The system obtains temperature data from a remote source,
# compares it with a given threshold and controls a remote heating
# unit by switching it on and off. It does so only within a time
# period configured on a remote service (or other source)
#
# This is purpose-built crap


class HeatingManagerImpl:
    @staticmethod
    def decide_required_action(current_temp: float, threshold_temp: float, is_active: bool) -> str:
        if not is_active:
            return "no action needed"
        else:
            return "on" if current_temp < threshold_temp else "off"

    ''' Observations about the initial design of this method:

        It's doing too many things at once.

        This method is responsible for immediately converting strings to floats, and does so without any error handling.
        This method is responsible for opening sockets and sending the actual decision.

    '''
    def manage_heating(self, t: str, threshold: str, active: bool):
        # TODO: error handling here
        f_t = float(t)
        f_threshold = float(threshold)

        required_action = HeatingManagerImpl.decide_required_action(f_t, f_threshold, active)
        if required_action is "no action needed":
            return

        # Send the actual decision over
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('heater.home', 9999))
            s.sendall(str.encode(required_action))
            s.close()
        except Exception:
            print('error connecting; failed to send {}'.format(required_action))


class ScheduleManager:
    def manage(self, h_m: HeatingManagerImpl, threshold: str):
        t = self.string_from_url("http://probe.home:9990/temp", 4)
        if datetime.datetime.now().time().hour > self.start_hour() and datetime.datetime.now().time().hour < self.end_hour():
            h_m.manage_heating(t, threshold, True)
        if datetime.datetime.now().time().hour < self.start_hour() or datetime.datetime.now().time().hour > self.end_hour():
            h_m.manage_heating(t, threshold, False)

    def end_hour(self) -> int:
        return int(self.string_from_url("http://timer.home:9990/end", 2))

    def string_from_url(self, url: str, s: int) -> str:
        r = requests.get(url)
        return r.text[:s]

    def start_hour(self) -> int:
        return int(self.string_from_url("http://timer.home:9990/start", 2))


# Actually using the class
heat_man_impl = HeatingManagerImpl()
heat_man_impl.manage_heating("20", "25", True)

print(HeatingManagerImpl.decide_required_action(20, 25, True))
print(HeatingManagerImpl.decide_required_action(20, 25, False))
