
#!/usr/bin/python3
#
#The recipe gives simple implementation of a Discrete Proportional-Integral-Derivative (PID) controller. PID controller gives output value for error between desired reference input and measurement feedback to minimize error value.
#More information: http://en.wikipedia.org/wiki/PID_controller
#
#cnr437@gmail.com
#
####### Example #########
#
#p=PID(3.0,0.4,1.2)
#p.setPoint(5.0)
#while True:
#     pid = p.update(measurement_value)
#
import time

class PID:
    """   Discrete PID control  """

    def __init__(self, P, I, D, Derivator=0, Integrator=0, Integrator_max=500, Integrator_min=-500, current_time=None):
      self.Kp=P
      self.Ki=I
      self.Kd=D
      self.Derivator=Derivator
      self.Integrator=Integrator
      self.Integrator_max=Integrator_max
      self.Integrator_min=Integrator_min
      self.sample_time = 0.00
      self.current_time = current_time if current_time is not None else time.time()
      self.last_time = self.current_time
      self.set_point=0.0
      self.error=0.0
      self.clear()

    def clear(self):
      """Clears PID computations and coefficients"""
      self.SetPoint = 0.0
      self.Kp = 0.0
      self.Ki = 0.0
      self.Kd = 0.0
      self.last_error = 0.0

    def update(self, current_value, current_time=None):
      """Calculates PID value for given reference feedback

      math::
      u(t) = K_p e(t) + K_i \int_{0}^{t} e(t)dt + K_d {de}/{dt}

      figure:: images/pid_1.png
      :align:   center

      Test PID with Kp=1.2, Ki=1, Kd=0.001 (test_pid.py)   """
      self.current_time = current_time if current_time is not None else time.time()
      delta_time = self.current_time - self.last_time
      delta_error = self.error - self.last_error

      if (delta_time >= self.sample_time):
        self.error = self.set_point - current_value
        self.P_value = self.Kp * self.error
        self.D_value = self.Kd * ( self.error - self.Derivator)
        self.Derivator = self.error
        self.Integrator = self.Integrator + self.error
        if self.Integrator > self.Integrator_max:
          self.Integrator = self.Integrator_max
        elif self.Integrator < self.Integrator_min:
          self.Integrator = self.Integrator_min
        self.I_value = self.Integrator * self.Ki
        PID = self.P_value + self.I_value + self.D_value
        self.last_time = self.current_time
        self.last_error = self.error
        return PID

#            self.output = self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)

    def setPoint(self,set_point):
        """
        Initilize the setpoint of PID
        """
        self.set_point = set_point
        self.Integrator=0
        self.Derivator=0

    def setIntegrator(self, Integrator):
        self.Integrator = Integrator

    def setDerivator(self, Derivator):
        self.Derivator = Derivator

        """Determines how aggressively the PID reacts to the current error with setting Proportional Gain"""
    def setKp(self,P):
        self.Kp=P

        """Determines how aggressively the PID reacts to the current error with setting Integral Gain"""
    def setKi(self,I):
        self.Ki=I

        """Determines how aggressively the PID reacts to the current error with setting Derivative Gain"""
    def setKd(self,D):
        self.Kd=D

    def getPoint(self):
        return self.set_point

    def getError(self):
        return self.error

    def getIntegrator(self):
        return self.Integrator

    def getDerivator(self):
        return self.Derivator

    def setSampleTime(self, sample_time):
        """PID that should be updated at a regular interval.
        Based on a pre-determined sampe time, the PID decides if it should compute or return immediately.
        """
        self.sample_time = sample_time



