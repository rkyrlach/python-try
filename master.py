from multiprocessing import Process, Queue, Lock
import threading, time
import lights;
import motor;
import server;

lq = Queue()
mq = Queue()
lights = lights.Lights()
motor  = motor.Motor()
server = server.Server()

if __name__ == '__main__':
  print("Hello")

  server_process = Process(target= server.start, args=(lq, mq, ))
  server_process.start()

  light_process = Process(target=lights.start, args=(lq, ))
  light_process.start()

  motor_process = Process(target=motor.startController, args=(mq, ))
  motor_process.start()

  done = False
  while (not done):
    time.sleep(1.0)
#    command = input("Lights or motor?")
#    if command == "lights":
    command = 'run'
    if (command == 'run' and  not lq.empty()):
      lqc = lq.get()
      print("light command = ", lqc)
      lq.put(lqc)
    elif (command == 'run' and not mq.empty()):             ### command == "motor":
      mqc = mq.get()
      print("motor command = ", mqc)
      mq.put(mqc)
    elif command == "quit":
      lq.put("quit")
      mq.put("quit")
      time.sleep(5)
      done = True
#    else:
#      print("I didn't recognize that command.", command)



