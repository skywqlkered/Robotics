class PID_controller:
    def __init__(self):
        self.P_term = 0
        self.I_term = 0
        self.D_term = 0

        self.error_rate = 0