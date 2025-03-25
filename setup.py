from setuptools import setup, find_packages

setup(
    name="train-ticket-auto-query",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.15.0",
    ],
    python_requires=">=3.8",
    description="火车票自动查询工具",
    author="Train Ticket Team",
) 