from setuptools import setup, find_packages

setup(
    name='docker-jar-diff',
    version='0.1.0',
    description='A tool to diff JAR files in Docker images',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    install_requires=[
        'click>=8.1,<9.0',
        'docker>=6.0,<7.0'
    ],
    extras_require={
        'dev': [
            'pytest>=7.3,<8.0'
        ]
    },
    entry_points={
        'console_scripts': [
            'docker-jar-diff=docker_jar_diff.cli:docker_jar_diff'
        ]
    },
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)