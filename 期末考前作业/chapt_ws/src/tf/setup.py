from setuptools import find_packages, setup

package_name = 'tf'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/tf.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='xiaofeiyu',
    maintainer_email='18020999493@163.com',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "tf_broadcaster=tf.tf_broadcaster:main",
            "gimbal_to_base=tf.gimbal_to_base:main"
        ],
    },
)
