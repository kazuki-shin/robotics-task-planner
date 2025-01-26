from setuptools import setup, find_packages

setup(
    name="robotics-task-planner",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.26.2",
        "pybullet>=3.2.5",
        "openai>=1.3.0",
        "python-dotenv>=1.0.0",
        "streamlit>=1.29.0",
        "tenacity>=8.2.3",
        "pyyaml>=6.0.1",
        "matplotlib>=3.8.2"
    ],
    python_requires=">=3.10",
) 