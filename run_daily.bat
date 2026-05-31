@echo off
echo Starting StockAI Daily Pipeline...
cd C:\Users\dell\Desktop\ai-stock-predictor
C:\Users\dell\Desktop\ai-stock-predictor\.venv-1\Scripts\python.exe backend/daily_runner.py
echo Completed! >> C:\Users\dell\Desktop\ai-stock-predictor\logs\daily_log.txt