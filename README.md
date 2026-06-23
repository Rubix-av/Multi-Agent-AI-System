# 🌍 AI Travel Planning System

An intelligent, multi-agent AI application that plans complete travel itineraries by autonomously gathering flight information, hotel options, and creating personalized travel schedules.

## 🎯 Project Overview

This project demonstrates how to build a sophisticated **Multi-Agent AI System** using LangGraph. The system consists of 4 specialized AI agents that work together seamlessly:

### Specialized Agents

- **✈️ Flight Agent**: Searches and retrieves real-time flight data using AviationStack API
- **🏨 Hotel Agent**: Discovers available hotels using Tavily Search API
- **🗓️ Itinerary Agent**: Creates personalized travel itineraries based on preferences
- **🤖 Final Response Agent**: Synthesizes all information into a comprehensive travel plan

## ✨ What You'll Learn

✅ Build a **Multi-Agent AI Application** using LangGraph  
✅ Implement **Agentic AI Architecture** step by step  
✅ Use **Llama 3.3 70B** model powered by Groq  
✅ Add **Memory Management** using PostgreSQL  
✅ Fetch **Real-time Flight Data** via AviationStack API  
✅ Search **Hotels** using Tavily Search API  
✅ Create a **Production-Ready Travel Planner**  
✅ Learn **Autonomous Agent Coordination**  

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **LLM Framework** | LangGraph |
| **Language Model** | Llama 3.3 70B (Groq) |
| **Database** | PostgreSQL |
| **Flight Data API** | AviationStack API |
| **Search Engine** | Tavily Search API |
| **Frontend** | Streamlit |
| **Language** | Python |

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL database
- Groq API Key (for Llama 3.3 70B access)
- AviationStack API Key
- Tavily Search API Key

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd multi_agent_ai_system
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:

```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# AviationStack API Configuration
AVIATIONSTACK_API_KEY=your_aviationstack_api_key_here

# Tavily Search API Configuration
TAVILY_API_KEY=your_tavily_api_key_here

# PostgreSQL Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=travel_planner
DB_USER=postgres
DB_PASSWORD=your_password_here
```

### 5. Setup PostgreSQL Database
```bash
# Create database
createdb travel_planner

# Run migrations (if applicable)
python scripts/init_db.py
```

## 📁 Project Structure

```
multi_agent_ai_system/
├── README.md
├── requirements.txt
├── .env.example
├── main.py
├── agents/
│   ├── flight_agent.py
│   ├── hotel_agent.py
│   ├── itinerary_agent.py
│   └── final_response_agent.py
├── tools/
│   ├── aviationstack_tool.py
│   ├── tavily_search_tool.py
│   └── database_tool.py
├── utils/
│   ├── database.py
│   ├── config.py
│   └── logger.py
├── app/
│   └── streamlit_app.py
└── scripts/
    └── init_db.py
```

## 🔧 Configuration

### Environment Setup
All API keys and database credentials should be set in the `.env` file. The application will automatically load these on startup.

### Database Schema
The PostgreSQL database stores:
- Travel history and preferences
- Agent responses and decisions
- User queries and results

## 🎮 Usage

### Run the Application
```bash
streamlit run app/streamlit_app.py
```

The Streamlit interface will open at `http://localhost:8501`

### Basic Usage Flow
1. Enter your travel details (destination, dates, preferences)
2. The system automatically:
   - Queries the Flight Agent for available flights
   - Fetches hotel options via the Hotel Agent
   - Creates an itinerary through the Itinerary Agent
   - Synthesizes everything via the Final Response Agent
3. Review your complete travel plan

## 🏗️ Architecture

### Agent Workflow

```
User Input
    ↓
[Flight Agent] → Real-time Flight Data (AviationStack)
    ↓
[Hotel Agent] → Hotel Search Results (Tavily)
    ↓
[Itinerary Agent] → Personalized Schedule
    ↓
[Final Response Agent] → Complete Travel Plan
    ↓
Output with Memory Stored (PostgreSQL)
```

### Agent Coordination
- **LangGraph** manages the workflow and coordination between agents
- **Groq's Llama 3.3 70B** powers each agent's decision-making
- **PostgreSQL** maintains conversation history and user preferences
- **APIs** provide real-time external data

## 💾 Memory Management

The system uses PostgreSQL to store:
- User preferences and travel history
- Agent reasoning steps and decisions
- API responses for caching
- Conversation logs for context

This enables the system to:
- Learn from past interactions
- Provide personalized recommendations
- Track booking decisions
- Improve over time

## 📡 API Integration

### AviationStack API
- Retrieves real-time flight information
- Updates availability and pricing
- Filters by route, date, and preferences

### Tavily Search API
- Searches for hotel accommodations
- Finds location-based information
- Gathers travel recommendations

## 🔐 Security Considerations

- Store sensitive API keys in `.env` file (never commit to git)
- Use `.gitignore` to exclude sensitive files
- Validate user inputs before processing
- Implement rate limiting for API calls
- Use parameterized queries for database operations

## 🐛 Troubleshooting

### Issue: "GROQ_API_KEY not found"
**Solution**: Ensure `.env` file exists and contains `GROQ_API_KEY=your_key`

### Issue: "Database connection failed"
**Solution**: Verify PostgreSQL is running and credentials in `.env` are correct

### Issue: "API rate limit exceeded"
**Solution**: Implement caching and add delays between API calls

## 📚 Learning Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Groq API Guide](https://console.groq.com/)
- [AviationStack API Docs](https://aviationstack.com/documentation)
- [Tavily Search API](https://tavily.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📄 License

This project is open source and available under the MIT License.

## 📧 Support

For questions or issues, please open an issue on the repository.

---

**Happy Planning! ✈️🏨🗺️**
