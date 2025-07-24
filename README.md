# 🔮 PredictMarket - Decentralized Prediction Markets on ICP

A full-stack Web3 prediction market application built on the Internet Computer Protocol (ICP), featuring AI-powered insights, automated market making (AMM), and a modern React frontend.

## 🌟 Features

### Core Functionality

- **📊 Prediction Markets**: Create and trade on binary outcome markets
- **🤖 AI Insights**: AI-generated market analysis with confidence scores and risk assessments
- **💱 Automated Market Maker**: LMSR-based pricing with dynamic liquidity
- **👤 User Profiles**: XP system, badges, and achievement tracking
- **🏆 Leaderboard**: Ranking system based on trading performance and accuracy
- **💬 Market Discussion**: Comment system for community engagement

### Technical Features

- **🔗 Multi-Wallet Support**: Plug Wallet, Stoic Wallet, and Internet Identity integration
- **⚡ Real-time Updates**: Live price feeds and market data
- **📱 Responsive Design**: Modern, mobile-first UI with TailwindCSS
- **🛡️ Type Safety**: Full TypeScript implementation
- **🧪 Testing**: Comprehensive test suite

## 🏗️ Architecture

### Backend (Rust Canisters)

- **Market Management**: Create, validate, and resolve prediction markets
- **Trading Engine**: AMM with LMSR pricing algorithm
- **User Management**: Profile system with XP and badges
- **AI Integration**: Placeholder for AI insight generation
- **Comments System**: Decentralized discussion threads

### Frontend (React + TypeScript)

- **Modern UI**: TailwindCSS with custom design system
- **State Management**: React hooks with efficient data fetching
- **Wallet Integration**: Multiple ICP wallet connectors
- **Responsive Design**: Mobile-first approach

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Rust and Cargo
- DFX (DFINITY SDK)
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd hack_icp
   ```

2. **Install dependencies**

   ```bash
   npm install
   cd src/frontend && npm install
   ```

3. **Start local IC replica**

   ```bash
   dfx start --background
   ```

4. **Deploy canisters**

   ```bash
   dfx deploy
   ```

5. **Start development server**

   ```bash
   npm start
   ```

6. **Open the application**
   Navigate to `http://localhost:5174` in your browser

## 📁 Project Structure

```
hack_icp/
├── src/
│   ├── backend/                 # Rust canister code
│   │   ├── src/lib.rs          # Main backend logic
│   │   └── Cargo.toml          # Rust dependencies
│   ├── frontend/               # React frontend
│   │   ├── src/
│   │   │   ├── components/     # Reusable UI components
│   │   │   ├── views/          # Page components
│   │   │   ├── services/       # API service layer
│   │   │   └── App.tsx         # Main app component
│   │   └── package.json        # Frontend dependencies
│   └── declarations/           # Generated TypeScript types
├── dfx.json                    # DFX configuration
└── package.json                # Workspace configuration
```

## 🎮 Usage Guide

### Creating Markets

1. Connect your wallet using the header button
2. Navigate to "Create Market"
3. Fill in market details:
   - Title (specific and clear)
   - Description (resolution criteria)
   - Category
   - Close date
4. Submit for validation
5. Markets go through AI review and admin validation

### Trading

1. Browse active markets on the homepage
2. Click on a market to view details
3. Review AI insights and community discussion
4. Choose YES or NO position
5. Enter trade amount
6. Confirm transaction

### Leaderboard

- Track top traders by XP and accuracy
- Earn XP through trading and market creation
- Unlock badges for achievements
- View detailed user profiles

## 🧠 AI Integration

The application includes placeholder AI functionality that can be integrated with external AI services:

- **Market Analysis**: Generate insights on market conditions
- **Risk Assessment**: Identify potential risks and uncertainties
- **Confidence Scoring**: Provide AI confidence levels
- **Market Validation**: Assist in reviewing new market proposals

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_DFX_NETWORK=local
VITE_CANISTER_ID_BACKEND=your-backend-canister-id
```

### Wallet Configuration

The application supports multiple wallet types:

- **Plug Wallet**: Browser extension wallet
- **Stoic Wallet**: Web-based wallet
- **Internet Identity**: Built-in ICP authentication

## 🧪 Testing

Run the test suite:

```bash
npm test
```

Backend tests:

```bash
npm run test:backend
```

Frontend tests:

```bash
npm run test:frontend
```

## 🚢 Deployment

### Local Development

```bash
dfx start --background
dfx deploy
npm start
```

### Production Deployment

```bash
dfx deploy --network ic
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Guidelines

- Follow TypeScript best practices
- Use the existing component structure
- Maintain responsive design principles
- Add comprehensive error handling
- Write tests for new features

## 📚 API Reference

### Backend Canister Methods

#### Markets

- `get_markets()` - Retrieve all markets
- `get_market(id: bigint)` - Get specific market
- `create_market(title, description, category, close_date)` - Create new market

#### Trading

- `buy_shares(market_id, is_yes, amount)` - Purchase market shares
- `get_market_trades(market_id)` - Get trade history

#### Users

- `get_user_profile(principal)` - Get user profile
- `get_leaderboard()` - Get top users

#### AI & Social

- `get_ai_insight(market_id)` - Get AI analysis
- `add_comment(market_id, content)` - Add market comment
- `get_market_comments(market_id)` - Get market discussion

## 🔮 Future Enhancements

- **NFT Badges**: On-chain achievement tokens
- **Advanced Charts**: Detailed price history visualization
- **Mobile App**: React Native implementation
- **Liquidity Pools**: Community-provided market liquidity
- **Oracle Integration**: External data source connectivity
- **Advanced AI**: Integration with sophisticated prediction models
- **Social Features**: Follow traders, copy trading strategies

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

1. Check the GitHub Issues page
2. Review the documentation
3. Join the community Discord
4. Contact the development team

## 🙏 Acknowledgments

- **Internet Computer Protocol** for the decentralized infrastructure
- **DFINITY Foundation** for the development tools and SDK
- **React** and **TailwindCSS** for the frontend framework
- The open-source community for inspiration and contributions

---

**Built with ❤️ for the decentralized future of prediction markets**
