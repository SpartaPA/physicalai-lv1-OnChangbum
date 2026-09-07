from setuptools import find_packages
from setuptools import setup
import os
from glob import glob

package_name = 'turtle_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pa4',
    maintainer_email='dhsckdqja@gmail.com',
    description='ROS2 Python Package for turtlesim control and monitoring',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'distance_publisher = turtle_py.distance_publisher:main',
            'distance_subscriber = turtle_py.distance_subscriber:main',
            'square_driver = turtle_py.square_driver:main',
            'turtle_tf_broadcaster = turtle_py.turtle_tf_broadcaster:main',
            'builtin_service_client = turtle_py.builtin_service_client:main',
            'toggle_server_node = turtle_py.toggle_server_node:main',
            'rotate_action_client = turtle_py.rotate_action_client:main',
            'polygon_action_server = turtle_py.polygon_action_server:main',
            'waypoint_publisher = turtle_py.waypoint_publisher:main',
            'sensor_qos_publisher = turtle_py.sensor_qos_publisher:main',
            'sensor_qos_subscriber = turtle_py.sensor_qos_subscriber:main',
        ],
    },
)
