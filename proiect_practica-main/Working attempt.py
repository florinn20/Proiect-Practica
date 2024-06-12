import socket
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

# Set pins 11 & 12 as outputs, and define as PWM servo1 & servo2
GPIO.setup(11,GPIO.OUT)
servo1 = GPIO.PWM(11,50) # pin 11 for servo1
GPIO.setup(15,GPIO.OUT)
servo2 = GPIO.PWM(15,50) # pin 12 for servo2

# Start PWM running on both servos, value of 0 (pulse off)
servo1.start(0)
servo2.start(0)
servo1.ChangeDutyCycle(7)
servo2.ChangeDutyCycle(2)
consecutiv=0
counter1=7
counter2=7.125

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    HOST='192.168.137.38'
    PORT=65324
    s.bind((HOST,PORT))
    s.listen(1)
    conn, addr= s.accept()
    with conn:
        print ("Server is connected")
        while True:
            data=conn.recv(2048).decode('utf-8')
            if data:
                print(data)
                x, y=data.split(",")
                print(x)
                print(y)
                
                if float(x)!=320 and float(y)!=240:
                
                    if float(x)>15 and float(x)<=45:
                        if(counter1!=12):
                            counter1+=0.2
                        servo1.ChangeDutyCycle(counter1)
                        time.sleep(0.1)
                        servo1.ChangeDutyCycle(0)
                                
                    if float(x)<-15 and float(x)>=-45:
                        if(counter1!=2):
                            counter1-=0.2
                        servo1.ChangeDutyCycle(counter1)
                        time.sleep(0.1)
                        servo1.ChangeDutyCycle(0)
                                
                    if float(x)>45:
                        if(counter1!=12):
                            counter1+=0.4
                        servo1.ChangeDutyCycle(counter1)
                        time.sleep(0.1)
                        servo1.ChangeDutyCycle(0)
                                
                    if float(x)<-45:
                        if(counter1!=2):
                            counter1-=0.4
                        servo1.ChangeDutyCycle(counter1)
                        time.sleep(0.1)
                        servo1.ChangeDutyCycle(0)
                                
                    if float(y)>10 and float(y)<=20:
                        if(counter2!=10):
                            counter2+=0.1
                        servo2.ChangeDutyCycle(counter2)
                        time.sleep(0.1)
                        servo2.ChangeDutyCycle(0)

                    if float(y)<-10 and float(y)>=-20:
                        if(counter2!=7):
                            counter2-=0.1
                        servo2.ChangeDutyCycle(counter2)
                        time.sleep(0.1)
                        servo2.ChangeDutyCycle(0)
                        
                    if float(y)>20:
                        if(counter2!=10):
                            counter2+=0.2
                        servo2.ChangeDutyCycle(counter2)
                        time.sleep(0.1)
                        servo2.ChangeDutyCycle(0)
                        
                    if float(y)<-20:
                        if(counter2!=10):
                            counter2-=0.2
                        servo2.ChangeDutyCycle(counter2)
                        time.sleep(0.1)
                        servo2.ChangeDutyCycle(0)
                        
                    consecutiv=0
                else:
                    if (float(x)==320 and float(y)==240 and consecutiv!=15):
                        consecutiv+=1
                    else:
                        servo1.ChangeDutyCycle(7)
                        time.sleep(0.1)
                        servo1.ChangeDutyCycle(0)
                        counter1=7
                        servo2.ChangeDutyCycle(7)
                        time.sleep(0.1)
                        servo2.ChangeDutyCycle(0)
                        counter2=7
                        consecutiv=15
                          
servo1.stop()
servo2.stop()
GPIO.cleanup()
            
