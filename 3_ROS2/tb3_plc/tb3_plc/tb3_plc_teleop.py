#!/usr/bin/env python3

#**************************************************************************
#
# Node to read Holding Registers from PLC MicroLogix 1400 via Modbus TCP 
# convert and publish them as values for the topic /cmd_vel to be read by
# mobile robot Turtlebot3 Burger.
#
# Author: Fernando Salinas
# Universidad Autónoma de Coahuila
# Facultad de Ingeniería Mecánica y Eléctrica
#
#**************************************************************************

import socket
import struct
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

PLC_IP = '192.168.8.10'
PLC_PORT = 502
UNIT_ID = 1
START = 0
COUNT = 12

def build_modbus_request(transaction_id, unit_id, start_address, quantity):
    return struct.pack('>HHHBBHH',
        transaction_id, 0, 6, unit_id, 3, start_address, quantity
    )

def parse_response(response):
    byte_count = response[8]
    return struct.unpack(f'>{byte_count//2}h', response[9:9+byte_count])

#Funcion que toma dos Holdings Registers del PLC y los convierte en un numero Float.
def to_float(integer_part, decimal_part):
    scale = 1000.0

    # Caso especial: número negativo entre -1.0 y 0.0
    if integer_part == 0 and decimal_part < 0:
        return decimal_part / scale

    # Número positivo o negativo menor a -1.0
    else:
        return integer_part + decimal_part / scale


class tb3_plc_teleop(Node):
    def __init__(self):
        super().__init__('tb3_plc_teleop')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(1.0, self.read_and_publish)

    def read_and_publish(self):
        try:
            with socket.create_connection((PLC_IP, PLC_PORT), timeout=3) as sock:
                request = build_modbus_request(1, UNIT_ID, START, COUNT)
                sock.sendall(request)
                response = sock.recv(1024)

                if not response:
                    self.get_logger().warn("Sin respuesta del PLC.")
                    return

                values = parse_response(response)

                # Crear mensaje Twist
                msg = Twist()
                msg.linear.x = to_float(values[0], values[1])
                msg.linear.y = to_float(values[2], values[3])
                msg.linear.z = to_float(values[4], values[5])
                msg.angular.x = to_float(values[6], values[7])
                msg.angular.y = to_float(values[8], values[9])
                msg.angular.z = to_float(values[10], values[11])

                self.publisher.publish(msg)
                self.get_logger().info(f"Publicando /cmd_vel: {msg}")

        except Exception as e:
            self.get_logger().error(f"Error Modbus: {e}")

def main():
    rclpy.init()
    node = tb3_plc_teleop()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
