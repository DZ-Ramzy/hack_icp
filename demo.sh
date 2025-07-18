#!/bin/bash

# Demo script for PredictMarket application
echo "🔮 PredictMarket Demo Setup"
echo "=========================="

# Check if dfx is running
if ! dfx ping > /dev/null 2>&1; then
    echo "Starting local IC replica..."
    dfx start --background
else
    echo "✅ IC replica is already running"
fi

# Build and deploy canisters
echo "🔨 Building and deploying canisters..."
dfx build
dfx deploy

# Start frontend development server
echo "🚀 Starting frontend development server..."
cd src/frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "🎉 Demo is ready!"
echo "📱 Frontend: http://localhost:5174/"
echo "🔧 Candid UI: http://localhost:4943/?canisterId=$(dfx canister id __Candid_UI)&id=$(dfx canister id backend)"
echo ""
echo "🌟 Features to test:"
echo "   • Browse prediction markets"
echo "   • View AI insights"
echo "   • Connect wallet (Internet Identity)"
echo "   • Create new markets"
echo "   • Trade on markets"
echo "   • Check leaderboard"
echo ""
echo "Press Ctrl+C to stop the demo"

# Wait for user to stop
trap "kill $FRONTEND_PID; exit" INT
wait
