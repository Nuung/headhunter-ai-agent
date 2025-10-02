@echo off
echo ========================================
echo Installing Required Packages
echo ========================================
echo.

python -m pip install --upgrade pip

echo Installing core packages...
python -m pip install streamlit

echo Installing LangChain packages...
python -m pip install langchain langchain-core langchain-upstage langgraph

echo Installing ML packages...
python -m pip install sentence-transformers torch faiss-cpu

echo Installing other dependencies...
python -m pip install psycopg2-binary python-dotenv tavily-python sqlalchemy

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.

pause
