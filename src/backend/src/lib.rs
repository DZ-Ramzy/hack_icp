use candid::{CandidType, Deserialize, Principal};
use ic_cdk::export_candid;
use ic_cdk::api::call::call;
use std::cell::RefCell;
use std::collections::HashMap;

// Market types and structures
#[derive(Clone, Debug, CandidType, Deserialize)]
pub struct Market {
    pub id: u64,
    pub title: String,
    pub description: String,
    pub category: String,
    pub creator: Principal,
    pub close_date: u64, // timestamp
    pub status: MarketStatus,
    pub yes_shares: u64,
    pub no_shares: u64,
    pub yes_liquidity: u64,
    pub no_liquidity: u64,
    pub total_volume: u64,
    pub created_at: u64,
    pub resolved_outcome: Option<bool>, // Some(true) = YES wins, Some(false) = NO wins, None = unresolved
}

#[derive(Clone, Debug, CandidType, Deserialize)]
pub enum MarketStatus {
    PendingValidation,
    Active,
    Closed,
    Resolved,
}

#[derive(Clone, Debug, CandidType, Deserialize)]
pub struct Trade {
    pub id: u64,
    pub market_id: u64,
    pub trader: Principal,
    pub is_yes: bool,
    pub shares: u64,
    pub price: u64,
    pub timestamp: u64,
}

#[derive(Clone, Debug, CandidType, Deserialize)]
pub struct UserProfile {
    pub principal: Principal,
    pub username: String,
    pub xp: u64,
    pub total_trades: u64,
    pub successful_predictions: u64,
    pub badges: Vec<String>,
    pub created_at: u64,
}

#[derive(Clone, Debug, CandidType, Deserialize)]
pub struct AIInsight {
    pub market_id: u64,
    pub summary: String,
    pub confidence: f64, // 0.0 to 1.0
    pub risks: Vec<String>,
    pub prediction_lean: Option<bool>, // Some(true) = leans YES, Some(false) = leans NO
    pub generated_at: u64,
}

#[derive(Clone, Debug, CandidType, Deserialize)]
pub struct MarketComment {
    pub id: u64,
    pub market_id: u64,
    pub author: Principal,
    pub content: String,
    pub timestamp: u64,
}

// LLM Communication structures
#[derive(Clone, Debug, CandidType, Deserialize)]
pub struct ChatMessageV0 {
    pub content: String,
    pub role: ChatRole,
}

#[derive(Clone, Debug, CandidType, Deserialize)]
pub enum ChatRole {
    #[serde(rename = "user")]
    User,
    #[serde(rename = "assistant")]
    Assistant,
    #[serde(rename = "system")]
    System,
}

#[derive(Clone, Debug, CandidType, Deserialize)]
pub struct ChatRequestV0 {
    pub model: String,
    pub messages: Vec<ChatMessageV0>,
}

// LLM Canister ID (replace with actual canister ID)
const LLM_CANISTER_ID: &str = "w36hm-eqaaa-aaaal-qr76a-cai";

// State management
thread_local! {
    static MARKETS: RefCell<HashMap<u64, Market>> = RefCell::new(HashMap::new());
    static TRADES: RefCell<Vec<Trade>> = const { RefCell::new(Vec::new()) };
    static USER_PROFILES: RefCell<HashMap<Principal, UserProfile>> = RefCell::new(HashMap::new());
    static AI_INSIGHTS: RefCell<HashMap<u64, AIInsight>> = RefCell::new(HashMap::new());
    static COMMENTS: RefCell<Vec<MarketComment>> = const { RefCell::new(Vec::new()) };
    static NEXT_MARKET_ID: RefCell<u64> = const { RefCell::new(1) };
    static NEXT_TRADE_ID: RefCell<u64> = const { RefCell::new(1) };
    static NEXT_COMMENT_ID: RefCell<u64> = const { RefCell::new(1) };
    static TREASURY: RefCell<u64> = const { RefCell::new(0) };
}

// Initialize with sample data
#[ic_cdk::init]
fn init() {
    let sample_markets = vec![
        Market {
            id: 1,
            title: "Will Bitcoin reach $150,000 by end of 2025?".to_string(),
            description: "This market resolves to YES if Bitcoin (BTC) reaches or exceeds $150,000 USD by December 31, 2025.".to_string(),
            category: "Cryptocurrency".to_string(),
            creator: Principal::anonymous(),
            close_date: 1767225600, // Dec 31, 2025
            status: MarketStatus::Active,
            yes_shares: 450,
            no_shares: 550,
            yes_liquidity: 4500,
            no_liquidity: 5500,
            total_volume: 2500,
            created_at: 1737273600, // Current time
            resolved_outcome: None,
        },
        Market {
            id: 2,
            title: "Will OpenAI release GPT-5 in 2025?".to_string(),
            description: "This market resolves to YES if OpenAI officially releases a model called GPT-5 during 2025.".to_string(),
            category: "Technology".to_string(),
            creator: Principal::anonymous(),
            close_date: 1767292799,
            status: MarketStatus::Active,
            yes_shares: 600,
            no_shares: 400,
            yes_liquidity: 6000,
            no_liquidity: 4000,
            total_volume: 1800,
            created_at: 1737273600,
            resolved_outcome: None,
        },
        Market {
            id: 3,
            title: "Will Tesla stock reach $500 by Q2 2025?".to_string(),
            description: "This market resolves to YES if Tesla (TSLA) stock price reaches or exceeds $500 USD before June 30, 2025.".to_string(),
            category: "Finance".to_string(),
            creator: Principal::anonymous(),
            close_date: 1767292799, 
            status: MarketStatus::Active,
            yes_shares: 300,
            no_shares: 700,
            yes_liquidity: 3000,
            no_liquidity: 7000,
            total_volume: 1200,
            created_at: 1737273600,
            resolved_outcome: None,
        },
    ];

    let sample_insights = vec![
        AIInsight {
            market_id: 1,
            summary: "Bitcoin has shown strong institutional adoption and macroeconomic factors favor crypto. However, regulatory uncertainty remains a risk.".to_string(),
            confidence: 0.72,
            risks: vec!["Regulatory crackdowns".to_string(), "Market volatility".to_string(), "Macro economic shifts".to_string()],
            prediction_lean: Some(true),
            generated_at: 1767292799,
        },
        AIInsight {
            market_id: 2,
            summary: "OpenAI is likely to continue their rapid development cycle. GPT-5 announcement is probable given competitive pressure from other AI companies.".to_string(),
            confidence: 0.65,
            risks: vec!["Technical setbacks".to_string(), "Compute resource limitations".to_string(), "Safety concerns".to_string()],
            prediction_lean: Some(true),
            generated_at: 1767292799,
        },
        AIInsight {
            market_id: 3,
            summary: "Tesla faces production challenges and increased EV competition. Stock price target seems ambitious given current market conditions.".to_string(),
            confidence: 0.58,
            risks: vec!["Production delays".to_string(), "Increased competition".to_string(), "Economic recession".to_string()],
            prediction_lean: Some(false),
            generated_at: 1737273600,
        },
    ];

    MARKETS.with(|markets| {
        let mut m = markets.borrow_mut();
        for market in sample_markets {
            m.insert(market.id, market);
        }
    });

    AI_INSIGHTS.with(|insights| {
        let mut ai = insights.borrow_mut();
        for insight in sample_insights {
            ai.insert(insight.market_id, insight);
        }
    });

    NEXT_MARKET_ID.with(|id| *id.borrow_mut() = 4);
}

// Market functions
#[ic_cdk::query]
fn get_markets() -> Vec<Market> {
    MARKETS.with(|markets| markets.borrow().values().cloned().collect())
}

#[ic_cdk::query]
fn get_market(id: u64) -> Option<Market> {
    MARKETS.with(|markets| markets.borrow().get(&id).cloned())
}

#[ic_cdk::update]
fn create_market(
    title: String,
    description: String,
    category: String,
    close_date: u64,
) -> Result<u64, String> {
    let caller = ic_cdk::caller();

    if title.is_empty() || description.is_empty() {
        return Err("Title and description cannot be empty".to_string());
    }

    let market_id = NEXT_MARKET_ID.with(|id| {
        let current_id = *id.borrow();
        *id.borrow_mut() = current_id + 1;
        current_id
    });

    let market = Market {
        id: market_id,
        title,
        description,
        category,
        creator: caller,
        close_date,
        status: MarketStatus::PendingValidation,
        yes_shares: 500, // Initial liquidity
        no_shares: 500,
        yes_liquidity: 5000,
        no_liquidity: 5000,
        total_volume: 0,
        created_at: ic_cdk::api::time(),
        resolved_outcome: None,
    };

    MARKETS.with(|markets| {
        markets.borrow_mut().insert(market_id, market);
    });

    Ok(market_id)
}

// AMM pricing function using LMSR (simplified)
fn calculate_price(yes_shares: u64, no_shares: u64, buy_yes: bool, amount: u64) -> u64 {
    let base_liquidity = 1000u64;

    if buy_yes {
        let price_impact = (amount * 1000) / (base_liquidity + yes_shares);
        500 + price_impact.min(450) // Price between 50-950 (0.05-0.95 in decimal)
    } else {
        let price_impact = (amount * 1000) / (base_liquidity + no_shares);
        500 - price_impact.min(450)
    }
}

#[ic_cdk::update]
fn buy_shares(market_id: u64, is_yes: bool, amount: u64) -> Result<Trade, String> {
    let caller = ic_cdk::caller();

    if amount == 0 {
        return Err("Amount must be greater than 0".to_string());
    }

    let trade_id = NEXT_TRADE_ID.with(|id| {
        let current_id = *id.borrow();
        *id.borrow_mut() = current_id + 1;
        current_id
    });

    let price = MARKETS.with(|markets| {
        let mut markets_map = markets.borrow_mut();
        if let Some(market) = markets_map.get_mut(&market_id) {
            if !matches!(market.status, MarketStatus::Active) {
                return Err("Market is not active".to_string());
            }

            let price = calculate_price(market.yes_shares, market.no_shares, is_yes, amount);

            // Update market state - liquidity should directly reflect the amount bet
            if is_yes {
                market.yes_shares += amount;
                market.yes_liquidity += amount; // Direct 1:1 relationship
            } else {
                market.no_shares += amount;
                market.no_liquidity += amount; // Direct 1:1 relationship
            }

            market.total_volume += amount;

            // Collect 2% fee on the amount bet
            let fee = (amount * 2) / 100;
            TREASURY.with(|treasury| {
                *treasury.borrow_mut() += fee;
            });

            Ok(price)
        } else {
            Err("Market not found".to_string())
        }
    })?;

    let trade = Trade {
        id: trade_id,
        market_id,
        trader: caller,
        is_yes,
        shares: amount,
        price,
        timestamp: ic_cdk::api::time(),
    };

    TRADES.with(|trades| {
        trades.borrow_mut().push(trade.clone());
    });

    // Update user profile XP
    USER_PROFILES.with(|profiles| {
        let mut profiles_map = profiles.borrow_mut();
        let profile = profiles_map.entry(caller).or_insert(UserProfile {
            principal: caller,
            username: format!(
                "User{}",
                caller.to_text().chars().take(8).collect::<String>()
            ),
            xp: 0,
            total_trades: 0,
            successful_predictions: 0,
            badges: vec![],
            created_at: ic_cdk::api::time(),
        });

        profile.total_trades += 1;
        profile.xp += amount / 10; // Gain XP for trading
    });

    Ok(trade)
}

#[ic_cdk::query]
fn get_market_trades(market_id: u64) -> Vec<Trade> {
    TRADES.with(|trades| {
        trades
            .borrow()
            .iter()
            .filter(|trade| trade.market_id == market_id)
            .cloned()
            .collect()
    })
}

#[ic_cdk::query]
fn get_user_profile(principal: Principal) -> Option<UserProfile> {
    USER_PROFILES.with(|profiles| profiles.borrow().get(&principal).cloned())
}

#[ic_cdk::query]
fn get_leaderboard() -> Vec<UserProfile> {
    USER_PROFILES.with(|profiles| {
        let mut users: Vec<_> = profiles.borrow().values().cloned().collect();
        users.sort_by(|a, b| b.xp.cmp(&a.xp));
        users.into_iter().take(20).collect()
    })
}

#[ic_cdk::update]
async fn get_ai_insight(market_id: u64) -> Option<AIInsight> {
    // First check if we have a cached insight
    let cached = AI_INSIGHTS.with(|insights| insights.borrow().get(&market_id).cloned());
    
    // If we have a recent cached insight (less than 1 hour old), return it
    if let Some(insight) = cached {
        let current_time = ic_cdk::api::time();
        let one_hour = 3600 * 1_000_000_000; // 1 hour in nanoseconds
        
        if current_time - insight.generated_at < one_hour {
            return Some(insight);
        }
    }
    
    // Get market data
    let market = MARKETS.with(|markets| markets.borrow().get(&market_id).cloned())?;
    
    // Create prompt for the AI agent
    let prompt = format!(
        "Analyze this prediction market and provide insights:
        
        Title: {}
        Description: {}
        Category: {}
        
        Current state:
        - Yes liquidity: {} ICP
        - No liquidity: {} ICP  
        - Total volume: {} ICP
        - Status: {:?}
        
        Please provide:
        1. A brief analysis summary (2-3 sentences)
        2. Your prediction (YES/NO) with confidence level (0-1)
        3. Key risk factors (list 2-3 main risks)
        
        Format your response as JSON with keys: summary, prediction, confidence, risks",
        market.title,
        market.description,
        market.category,
        market.yes_liquidity as f64 / 100_000_000.0,
        market.no_liquidity as f64 / 100_000_000.0,
        market.total_volume as f64 / 100_000_000.0,
        market.status
    );
    
    // Create chat request
    let chat_request = ChatRequestV0 {
        model: "gpt-4o-mini".to_string(), // or whatever model you're using
        messages: vec![
            ChatMessageV0 {
                role: ChatRole::System,
                content: "You are an expert financial analyst specializing in prediction markets. Provide clear, objective analysis based on market data.".to_string(),
            },
            ChatMessageV0 {
                role: ChatRole::User, 
                content: prompt,
            }
        ],
    };
    
    // For testing purposes, let's create a mock AI response first
    // TODO: Remove this when the LLM canister is properly accessible
    let market_title = MARKETS.with(|markets| {
        markets.borrow().get(&market_id).map(|m| m.title.clone()).unwrap_or_default()
    });
    
    let mock_insight = AIInsight {
        market_id,
        summary: format!(
            "🤖 AI Analysis for '{}': Based on current market trends and sentiment analysis, this prediction market shows interesting dynamics. The market sentiment appears to be driven by recent news and social media discussions. Consider both bullish and bearish scenarios before making investment decisions.",
            market_title
        ),
        confidence: 0.75,
        risks: vec![
            "Market volatility due to external events".to_string(),
            "Limited trading volume may affect price discovery".to_string(),
            "Information asymmetry between participants".to_string(),
        ],
        prediction_lean: Some(true), // Slightly bullish
        generated_at: ic_cdk::api::time(),
    };
    
    // Cache the mock insight
    AI_INSIGHTS.with(|insights| {
        insights.borrow_mut().insert(market_id, mock_insight.clone());
    });
    
    return Some(mock_insight);
    
    // Call the LLM canister
    match Principal::from_text(LLM_CANISTER_ID) {
        Ok(llm_principal) => {
            let response: Result<(String,), _> = call(llm_principal, "v0_chat", (chat_request,)).await;
            
            match response {
                Ok((ai_response,)) => {
                    // Parse the AI response and create AIInsight
                    let insight = parse_ai_response(&ai_response, market_id);
                    
                    // Cache the insight
                    if let Some(ref insight_to_cache) = insight {
                        AI_INSIGHTS.with(|insights| {
                            insights.borrow_mut().insert(market_id, insight_to_cache.clone());
                        });
                    }
                    
                    insight
                },
                Err(e) => {
                    // Fallback to a default insight if AI call fails
                    Some(AIInsight {
                        market_id,
                        summary: format!("AI analysis call failed: {:?}. Your Python agent may be offline or unreachable.", e),
                        confidence: 0.3,
                        risks: vec!["AI analysis temporarily unavailable".to_string(), "Check Python agent status".to_string()],
                        prediction_lean: None,
                        generated_at: ic_cdk::api::time(),
                    })
                }
            }
        },
        Err(_) => {
            // Invalid canister ID
            Some(AIInsight {
                market_id,
                summary: "Invalid LLM canister ID configuration. Please check the setup.".to_string(),
                confidence: 0.1,
                risks: vec!["Configuration error".to_string()],
                prediction_lean: None,
                generated_at: ic_cdk::api::time(),
            })
        }
    }
}

// Helper function to parse AI response
fn parse_ai_response(response: &str, market_id: u64) -> Option<AIInsight> {
    // Try to parse JSON response from AI
    // This is a simplified parser - you might want to use a proper JSON library
    
    // For now, create a basic insight with the raw response
    // You can enhance this to properly parse JSON
    Some(AIInsight {
        market_id,
        summary: response.to_string(),
        confidence: 0.7, // Default confidence
        risks: vec!["Market volatility".to_string(), "Unexpected events".to_string()],
        prediction_lean: None, // Parse from response
        generated_at: ic_cdk::api::time(),
    })
}

#[ic_cdk::update]
fn add_comment(market_id: u64, content: String) -> Result<u64, String> {
    let caller = ic_cdk::caller();

    if content.is_empty() || content.len() > 500 {
        return Err("Comment must be between 1 and 500 characters".to_string());
    }

    let comment_id = NEXT_COMMENT_ID.with(|id| {
        let current_id = *id.borrow();
        *id.borrow_mut() = current_id + 1;
        current_id
    });

    let comment = MarketComment {
        id: comment_id,
        market_id,
        author: caller,
        content,
        timestamp: ic_cdk::api::time(),
    };

    COMMENTS.with(|comments| {
        comments.borrow_mut().push(comment);
    });

    Ok(comment_id)
}

#[ic_cdk::query]
fn get_market_comments(market_id: u64) -> Vec<MarketComment> {
    COMMENTS.with(|comments| {
        comments
            .borrow()
            .iter()
            .filter(|comment| comment.market_id == market_id)
            .cloned()
            .collect()
    })
}

#[ic_cdk::query]
fn get_treasury_balance() -> u64 {
    TREASURY.with(|treasury| *treasury.borrow())
}

export_candid!();
