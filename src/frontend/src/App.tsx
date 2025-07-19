import { useState } from "react";
import { Header, Footer } from "./components";
import {
  HomeView,
  MarketView,
  CreateMarketView,
  LeaderboardView,
} from "./views";

type Page = "home" | "market" | "create" | "leaderboard";

function App() {
  const [currentPage, setCurrentPage] = useState<Page>("home");
  const [selectedMarketId, setSelectedMarketId] = useState<bigint | null>(null);

  const handleNavigate = (page: string) => {
    const validPage = page as Page;
    setCurrentPage(validPage);
    if (validPage !== "market") {
      setSelectedMarketId(null);
    }
  };

  const handleMarketSelect = (marketId: bigint) => {
    setSelectedMarketId(marketId);
    setCurrentPage("market");
  };

  const handleMarketCreated = (marketId: bigint) => {
    setSelectedMarketId(marketId);
    setCurrentPage("market");
  };

  const handleBackToHome = () => {
    setCurrentPage("home");
    setSelectedMarketId(null);
  };

  const renderCurrentPage = () => {
    switch (currentPage) {
      case "home":
        return <HomeView onMarketSelect={handleMarketSelect} />;
      case "market":
        if (!selectedMarketId) {
          handleNavigate("home");
          return null;
        }
        return (
          <MarketView marketId={selectedMarketId} onBack={handleBackToHome} />
        );
      case "create":
        return <CreateMarketView onMarketCreated={handleMarketCreated} />;
      case "leaderboard":
        return <LeaderboardView />;
      default:
        return <HomeView onMarketSelect={handleMarketSelect} />;
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-gray-50">
      <Header currentPage={currentPage} onNavigate={handleNavigate} />
      <main className="flex-1">{renderCurrentPage()}</main>
      <Footer />
    </div>
  );
}

export default App;
