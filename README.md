# Robotics Task Planning System

An AI-powered system that translates natural language instructions into executable robot actions, making robotics more accessible to non-technical users.

## Features

- Natural language command processing
- AI-powered task decomposition
- Automated code generation for robot control
- PyBullet simulation integration
- Web-based user interface

## Prerequisites

- Python 3.10 or higher
- OpenAI API key with active billing
- 16GB RAM minimum
- GPU recommended (optional)
- Stable internet connection
- Anaconda or Miniconda installed

## API Setup

1. Create an OpenAI account at https://platform.openai.com/signup
2. Set up billing at https://platform.openai.com/account/billing
3. Create an API key at https://platform.openai.com/api-keys
4. Add your API key to the .env file:
```bash
OPENAI_API_KEY=your_api_key_here
```

Note: Make sure your OpenAI account has:
- A valid payment method
- Available credit
- API access enabled

## Quick Start

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/robotics-task-planner.git
cd robotics-task-planner

# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies and create virtual environment
poetry install

# Activate the virtual environment
poetry shell

# Run the application
poetry run streamlit run src/ui/app.py
```

## Project Structure

```
robotics-task-planner/
├── src/                    # Source code directory
│   ├── core/              # Core logic modules
│   │   ├── task_planner.py
│   │   ├── code_generator.py
│   │   └── prompt_templates.py
│   ├── simulation/        # PyBullet simulation
│   │   ├── robot_environment.py
│   │   └── robot_actions.py
│   ├── ui/               # User interface
│   │   └── app.py
│   └── utils/            # Utility functions
│       ├── logging.py
│       └── error_handler.py
├── tests/                # Test suite
│   ├── test_task_planner.py
│   ├── test_code_generator.py
│   └── test_simulation.py
├── configs/             # Configuration files
│   └── settings.yaml
├── logs/               # Application logs
├── docs/              # Documentation
├── requirements.txt
├── .env
└── README.md
```

## Usage

1. Install the package in development mode:
```bash
pip install -e .
```

2. Start the web interface:
```bash
streamlit run src/ui/app.py
```

# Alternative method using PYTHONPATH:
```bash
PYTHONPATH=$PWD streamlit run src/ui/app.py
```

2. Enter natural language commands in the interface, such as:
- "Pick up the red cube and place it on the blue platform"
- "Move the robot arm to coordinates (1, 2, 3)"
- "Rotate the gripper 90 degrees clockwise"

## Development

Run tests:
```bash
# Make sure you're in the conda environment
conda activate robotenv

# Run tests with the conda Python interpreter explicitly
python -m pytest tests/
```

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request