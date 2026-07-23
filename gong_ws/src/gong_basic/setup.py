import os
from glob import glob

from setuptools import find_packages, setup

package_name = "gong_basic"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", glob(os.path.join("launch", "*.launch.py"))),
        ("share/" + package_name + "/param", glob(os.path.join("param", "*.yaml"))),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="choi su gil",
    maintainer_email="freshmea@naver.com",
    description="gongju university ROS2 basic library",
    license="Apache 2.0",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "simple_pub = gong_basic.simple_pub:main",
            "class_pub = gong_basic.class_pub:main",
            "class_sub = gong_basic.class_sub:main",
            "header_pub = gong_basic.header_pub:main",
            "mpub = gong_basic.mpub:main",
            "tpub = gong_basic.tpub:main",
            "msub = gong_basic.msub:main",
            "m2sub = gong_basic.m2sub:main",
            "mtsub = gong_basic.mtsub:main",
            "mv_turtle = gong_basic.mv_turtle:main",
            "qos_test_pub = gong_basic.qos_test_pub:main",
            "qos_test_sub = gong_basic.qos_test_sub:main",
            "user_int_pub = gong_basic.user_int_pub:main",
            "service_server = gong_basic.service_server:main",
            "service_thread_server = gong_basic.service_thread_server:main",
            "service_client = gong_basic.service_client:main",
            "my_param = gong_basic.my_param:main",
            "param_async = gong_basic.param_async:main",
            "action_server = gong_basic.action_server:main",
            "action_client = gong_basic.action_client:main",
        ],
    },
)