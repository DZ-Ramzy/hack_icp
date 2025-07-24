import { useState } from "react";
import { Header } from "./components";
import { ModernFooter } from "./components/ModernFooter";
import {
  PolysMarketHome,
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
        return <PolysMarketHome />;
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
        return <PolysMarketHome />;
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-white">
      <Header currentPage={currentPage} onNavigate={handleNavigate} />
      <main className="animate-fade-in flex-1">{renderCurrentPage()}</main>
      <ModernFooter />
    </div>
  );
}

export default App;
