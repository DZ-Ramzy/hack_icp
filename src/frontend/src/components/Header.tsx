import { useState, useEffect } from "react";
import { AuthService, type AuthState } from "../services/auth";

interface HeaderProps {
  currentPage: string;
  onNavigate: (page: string) => void;
}

export function Header({ currentPage, onNavigate }: HeaderProps) {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    principal: null,
    identity: null,
  });
  const [showWalletMenu, setShowWalletMenu] = useState(false);

  useEffect(() => {
    // Initialize auth state
    AuthService.getAuthState().then(setAuthState);

    // Listen for auth changes
    AuthService.addAuthListener(setAuthState);

    return () => {
      AuthService.removeAuthListener(setAuthState);
    };
  }, []);

  const handleLogin = async () => {
    const success = await AuthService.login();
    if (success) {
      console.log("Login successful");
    }
  };

  const handleLogout = async () => {
    await AuthService.logout();
  };

  const handleWalletConnect = async (walletType: "plug" | "stoic") => {
    const success = await AuthService.connectWallet(walletType);
    if (success) {
      setShowWalletMenu(false);
    }
  };

  const getPrincipalShort = () => {
    if (!authState.principal) return "";
    const principalText = authState.principal.toString();
    return `${principalText.slice(0, 8)}...${principalText.slice(-4)}`;
  };

  return (
    <header className="border-b border-gray-200 bg-white shadow-sm">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo and Navigation */}
          <div className="flex items-center space-x-8">
            <div
              className="flex cursor-pointer items-center"
              onClick={() => onNavigate("home")}
            >
              <div className="bg-primary-500 flex h-8 w-8 items-center justify-center rounded-lg">
                <span className="text-sm font-bold text-white">CP</span>
              </div>
              <span className="ml-2 text-xl font-bold text-gray-900">
                ChainPredict ICP
              </span>
            </div>

            <nav className="hidden space-x-6 md:flex">
              <button
                onClick={() => onNavigate("home")}
                className={`rounded-md px-3 py-2 text-sm font-medium ${
                  currentPage === "home"
                    ? "bg-primary-100 text-primary-700"
                    : "text-gray-500 hover:bg-gray-100 hover:text-gray-700"
                }`}
              >
                Markets
              </button>
              <button
                onClick={() => onNavigate("create")}
                className={`rounded-md px-3 py-2 text-sm font-medium ${
                  currentPage === "create"
                    ? "bg-primary-100 text-primary-700"
                    : "text-gray-500 hover:bg-gray-100 hover:text-gray-700"
                }`}
              >
                Create Market
              </button>
              <button
                onClick={() => onNavigate("leaderboard")}
                className={`rounded-md px-3 py-2 text-sm font-medium ${
                  currentPage === "leaderboard"
                    ? "bg-primary-100 text-primary-700"
                    : "text-gray-500 hover:bg-gray-100 hover:text-gray-700"
                }`}
              >
                Leaderboard
              </button>
            </nav>
          </div>

          {/* Auth Section */}
          <div className="flex items-center space-x-4">
            {authState.isAuthenticated ? (
              <div className="flex items-center space-x-3">
                <span className="text-sm text-gray-600">
                  {getPrincipalShort()}
                </span>
                <button
                  onClick={handleLogout}
                  className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-200"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <button
                    onClick={() => setShowWalletMenu(!showWalletMenu)}
                    className="bg-primary-600 hover:bg-primary-700 rounded-lg px-4 py-2 text-sm font-medium text-white transition-colors"
                  >
                    Connect Wallet
                  </button>

                  {showWalletMenu && (
                    <div className="absolute right-0 z-50 mt-2 w-48 rounded-lg border border-gray-200 bg-white shadow-lg">
                      <button
                        onClick={() => handleWalletConnect("plug")}
                        className="w-full rounded-t-lg px-4 py-3 text-left text-sm text-gray-700 hover:bg-gray-50"
                      >
                        Plug Wallet
                      </button>
                      <button
                        onClick={() => handleWalletConnect("stoic")}
                        className="w-full px-4 py-3 text-left text-sm text-gray-700 hover:bg-gray-50"
                      >
                        Stoic Wallet
                      </button>
                      <button
                        onClick={handleLogin}
                        className="w-full rounded-b-lg border-t border-gray-100 px-4 py-3 text-left text-sm text-gray-700 hover:bg-gray-50"
                      >
                        Internet Identity
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
