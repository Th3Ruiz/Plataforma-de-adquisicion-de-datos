import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
import paho.mqtt.client as mqtt
import json

# Constante para convertir 'g' a m/s^2
G_A_METROS_S2 = 9.80665

class MQTTPuente(Node):
    def __init__(self):
        super().__init__('mqtt_a_ros_puente')
        
        # Este nodo publica en el tópico de entrada del filtro
        self.publisher_ = self.create_publisher(Imu, '/imu/data_raw', 10)
        
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect("localhost", 1883, 60)
        self.mqtt_client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        self.get_logger().info("Puente conectado al broker MQTT")
        client.subscribe("mpu9250/raw") # Escucha el tópico del ESP32

    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            
            acc_g = data["accel"]
            gyro_rads = data["gyro"]

            imu_msg_raw = Imu()
            imu_msg_raw.header.stamp = self.get_clock().now().to_msg()
            imu_msg_raw.header.frame_id = "imu_link"

            # Dejar la orientación vacía (el filtro la calculará)
            imu_msg_raw.orientation_covariance[0] = -1.0 # -1 significa "desconocida"

            # Llenar la Velocidad Angular (ESP32 ya la envía en rad/s)
            imu_msg_raw.angular_velocity.x = float(gyro_rads[0])
            imu_msg_raw.angular_velocity.y = float(gyro_rads[1])
            imu_msg_raw.angular_velocity.z = float(gyro_rads[2])
            imu_msg_raw.angular_velocity_covariance[0] = 0.0 # Asumir covarianza baja

            # Llenar Aceleración Lineal (CONVERTIR g a m/s^2)
            imu_msg_raw.linear_acceleration.x = float(acc_g[0]) * G_A_METROS_S2
            imu_msg_raw.linear_acceleration.y = float(acc_g[1]) * G_A_METROS_S2
            imu_msg_raw.linear_acceleration.z = float(acc_g[2]) * G_A_METROS_S2
            imu_msg_raw.linear_acceleration_covariance[0] = 0.0 # Asumir covarianza baja

            # Publicar en el tópico de ROS2
            self.publisher_.publish(imu_msg_raw)
            self.get_logger().info('Publicando datos crudos en /imu/data_raw')

        except Exception as e:
            self.get_logger().error(f'Error al procesar mensaje MQTT: {e}')

def main(args=None):
    rclpy.init(args=args)
    mqtt_puente_node = MQTTPuente()
    rclpy.spin(mqtt_puente_node)
    mqtt_puente_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()