from setuptools import setup, find_packages

setup(
    name="robotics-task-planner",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.26.2",
        "pytest>=7.4.3",
        "streamlit>=1.28.0",
        "langchain>=0.1.0",
        "langchain-openai>=0.0.1",
        "openai>=1.3.0",
        "typing-extensions",
        "python-dotenv",
        "matplotlib>=3.8.0"
    ]
) 