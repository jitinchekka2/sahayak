#!/bin/bash

# Sahayak Parent-Teacher Meeting Assistant Startup Script
# This script starts the enhanced API with meeting features

echo "🏫 Starting Sahayak Parent-Teacher Meeting Assistant..."
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the sahayak project directory"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if synthetic data exists, if not generate it
if [ ! -f "synthetic_students.json" ]; then
    echo "📊 No synthetic data found. Generating test data..."
    python3 generate_synthetic_data.py
    echo "✅ Test data generated successfully!"
else
    echo "✅ Synthetic data found"
fi

# Check if talking points sample exists
if [ ! -f "sample_talking_points.json" ]; then
    echo "🤖 Generating sample AI talking points..."
    python3 ai_talking_points.py
    echo "✅ Sample talking points generated!"
else
    echo "✅ Sample talking points found"
fi

echo ""
echo "🚀 Starting the enhanced Flask server..."
echo ""
echo "Available interfaces:"
echo "   🏠 Main Chat Interface:     http://localhost:5000/"
echo "   📋 Meeting Dashboard:       http://localhost:5000/meeting_dashboard.html"
echo ""
echo "API Endpoints:"
echo "   📚 Students API:            http://localhost:5000/api/students"
echo "   🤖 Talking Points:          http://localhost:5000/api/students/{id}/talking-points"
echo "   🎯 Generate Data:           http://localhost:5000/api/generate-synthetic-data"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="
echo ""

# Start the enhanced API
python3 main.py
