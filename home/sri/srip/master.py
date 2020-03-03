from multiprocessing import Process, Queue, Lock
import threading, time
import lights;              ### python3 DMX controller
import motor;               ### python3 VESC controller
import server;              ### python3 wifi server

lq = Queue()                ### queue for light commands from client
mq = Queue()                ### queue for motor commands from client
cq = Queue()                ### queue for any and all commands from client
qs = Queue()                ### queue for status reporting to the client

lights = lights.Lights()    ### light (DMX) controller
motor  = motor.Motor()      ### motor (VESC) controller
server = server.Server()    ### wifi server to talk to "Lane" client

if __name__ == '__main__':
  print("Hello Russ")       ### temporary message to Russ

  server_process = Process(target= server.start, args=(lq, mq, cq, qs, ))
  server_process.start()    ### start the wifi server

  light_process = Process(target=lights.start, args=(lq, ))
  light_process.start()     ### start the DMX processor

  motor_process = Process(target=motor.startController, args=(mq, qs,))
  motor_process.start()     ### start the VESC processor

  done = False
  while (not done):
    time.sleep(0.1)
    while (not cq.empty()):
      command = cq.get(); print(" *** cmd = ",command, command[0])
      if (command[0] == 99):     ###  and  not lq.empty()):    ### light command
        lqc = lq.get()
        print(" *** light command = ", lqc)
        lq.put(lqc)
      elif (command[0] == 116):  ###  and not mq.empty()):   ### motor command
        mqc = mq.get()
        print(" *** motor command = ", mqc)
        mq.put(mqc)
      elif command[0] == 113:    ### q for quit
        lq.put("quit")
        mq.put("quit")
        time.sleep(5)
        done = True
      else:
        print("I didn't recognize that command.", command)



