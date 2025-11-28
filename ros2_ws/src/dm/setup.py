from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'dm'

setup(
    name=package_name,
    version='0.0.2',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Si tienes archivos JSON de configuración, descomenta esta línea:
        # (os.path.join('share', package_name, 'config'), glob('config/*.json')),
    ],
    install_requires=[
        'setuptools',
        'paho-mqtt'  # Cliente MQTT para Python
    ],
    zip_safe=True,
    maintainer='th3ruiz',
    maintainer_email='th3ruiz@example.com',
    description='ROS 2 package for receiving, processing, and publishing MPU9250 sensor data via MQTT',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'publicador_i = dm.publicador_i:main',
            'canales = dm.canales:main',
            'treshold = dm.treshold:main',
            'ras = dm.ras:main',
            'sus = dm.sus:main',
            'arucorviz=dm.arucorviz:main'
        ],
    },
)
