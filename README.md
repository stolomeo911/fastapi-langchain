## Getting Started

### Prerequisites

- Python 3.11
- Poetry (cmd installation: pip install poetry)
- Docker (optional, for containerized deployment)
- Make (optional to use make cmd)

### Installation

1. Clone the repository:

   ```sh
   git clone <repository_url>
   ```

2. Install dependencies:
   
   #### install backend env
   ```sh
   poetry -C backend/pandasai_app install
   ```
   
   #### install frontend env
   ```sh
   poetry -C frontend/app install
   ```

3. Set up the Python path:

   ```sh
   export PYTHONPATH=path-to-repository
   ```

4. Setup env variables:
   ```sh
   export GPT_API_KEY=your-api-key (set with '' if missing)
   export PANDASAI_API_KE=your-api-key (link to set key https://www.pandabi.ai/auth/sign-in)
   ```
   
### Usage

#### Running the Application

1. Run backend:

   ```sh
   make run_backend
   ```

2. Run front end:

   ```sh
   make streamlit run frontend/app/main.py
   ```

#### Training the Agent

1. Train the agent:

   ```sh
   make training_agent
   ```