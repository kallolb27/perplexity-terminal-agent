# Week 2 Submission: Autonomous Research Agent

## 🛠️ Setup Instructions & Dependencies

To run this Perplexity-style AI terminal locally, you need to configure your environment and install the required dependencies.

### 1. Install Python Dependencies
Ensure you have Python 3.8+ installed. Run the following command to install the required libraries:
`pip install openai requests trafilatura python-dotenv textual`

*Note: `trafilatura` is used for clean web scraping, and `textual` powers the terminal UI.*

### 2. Configure Environment Variables
You must provide your own API keys for the LLM and the search engine. Create a `.env` file in the root directory of this project and add the following keys:

OPENROUTER_API_KEY=your_openrouter_api_key_here
SERPER_API_KEY=your_serper_dev_api_key_here

### 3. Run the Application
Once dependencies are installed and the `.env` file is saved, run the agent from your terminal:

`python week_2/project/agent.py`

*(Adjust the file path if you are running it from a different working directory).*