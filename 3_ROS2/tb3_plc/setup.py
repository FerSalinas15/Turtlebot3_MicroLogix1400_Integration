from setuptools import find_packages, setup

package_name = 'tb3_plc'

setup(
    name=package_name,
    version='0.0.1',  # Versión actualizada
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Fernando Salinas',
    maintainer_email='fsalinas89@proton.me',
    description='Nodo que lee datos del TurtleBot3 y los envía al PLC MicroLogix 1400 por Modbus TCP.',
    license='MIT',  # Licencia recomendada
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'tb3_plc_teleop = tb3_plc.tb3_plc_teleop:main'  # Ejecutar el nodo
        ],
    },
)

