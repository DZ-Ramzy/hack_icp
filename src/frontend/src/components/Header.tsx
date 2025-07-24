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
  const [showMobileMenu, setShowMobileMenu] = useState(false);

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

  const navItems = [
    { id: "home", label: "Markets", icon: "📊" },
    { id: "create", label: "Create", icon: "+" },
    { id: "leaderboard", label: "Leaderboard", icon: "🏆" },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-gray-200 bg-white">
      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo Section - Style Polymarket */}
          <div className="flex items-center">
            <div
              className="flex cursor-pointer items-center"
              onClick={() => onNavigate("home")}
            >
              <div className="bg-primary-purple flex h-8 w-8 items-center justify-center rounded-lg">
                <span className="text-sm font-bold text-white">C</span>
              </div>
              <span className="ml-2 text-xl font-bold text-gray-900">
                ChainPredict
              </span>
            </div>

            {/* Desktop Navigation - Style Polymarket */}
            <nav className="ml-10 hidden lg:flex lg:space-x-8">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => onNavigate(item.id)}
                  className={`flex items-center space-x-1 px-3 py-2 text-sm font-medium transition-colors ${
                    currentPage === item.id
                      ? "text-primary-purple"
                      : "text-gray-500 hover:text-gray-900"
                  }`}
                >
                  <span>{item.label}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Auth Section - Style Polymarket */}
          <div className="flex items-center space-x-4">
            {/* Mobile Menu Button */}
            <button
              onClick={() => setShowMobileMenu(!showMobileMenu)}
              className="rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 lg:hidden"
            >
              <svg
                className="h-6 w-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                {showMobileMenu ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>

            {authState.isAuthenticated ? (
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2">
                  <div className="h-2 w-2 rounded-full bg-green-500"></div>
                  <span className="font-mono text-sm text-gray-700">
                    {getPrincipalShort()}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="text-sm text-gray-500 hover:text-gray-700"
                >
                  Sign out
                </button>
              </div>
            ) : (
              <div className="relative">
                <button
                  onClick={() => setShowWalletMenu(!showWalletMenu)}
                  className="bg-primary-purple hover:bg-primary-purple/90 rounded-lg px-4 py-2 text-sm font-medium text-white"
                >
                  Connect wallet
                </button>

                {showWalletMenu && (
                  <div className="absolute right-0 z-50 mt-2 w-72 rounded-lg border border-gray-200 bg-white shadow-lg">
                    <div className="p-4">
                      <h3 className="mb-3 text-sm font-medium text-gray-900">
                        Connect your wallet
                      </h3>
                      <div className="space-y-2">
                        <button
                          onClick={() => handleWalletConnect("plug")}
                          className="flex w-full items-center space-x-3 rounded-lg border border-gray-200 p-3 text-left hover:bg-gray-50"
                        >
                          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-500">
                            <span className="text-sm font-bold text-white">
                              P
                            </span>
                          </div>
                          <div className="flex-1">
                            <div className="text-sm font-medium text-gray-900">
                              Plug Wallet
                            </div>
                            <div className="text-xs text-gray-500">
                              Browser extension
                            </div>
                          </div>
                        </button>

                        <button
                          onClick={() => handleWalletConnect("stoic")}
                          className="flex w-full items-center space-x-3 rounded-lg border border-gray-200 p-3 text-left hover:bg-gray-50"
                        >
                          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-500">
                            <span className="text-sm font-bold text-white">
                              S
                            </span>
                          </div>
                          <div className="flex-1">
                            <div className="text-sm font-medium text-gray-900">
                              Stoic Wallet
                            </div>
                            <div className="text-xs text-gray-500">
                              Web-based wallet
                            </div>
                          </div>
                        </button>

                        <button
                          onClick={handleLogin}
                          className="flex w-full items-center space-x-3 rounded-lg border border-gray-200 p-3 text-left hover:bg-gray-50"
                        >
                          <div className="bg-primary-purple flex h-10 w-10 items-center justify-center rounded-lg">
                            <span className="text-sm font-bold text-white">
                              II
                            </span>
                          </div>
                          <div className="flex-1">
                            <div className="text-sm font-medium text-gray-900">
                              Internet Identity
                            </div>
                            <div className="text-xs text-gray-500">
                              Decentralized auth
                            </div>
                          </div>
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Mobile Menu - Style Polymarket */}
        {showMobileMenu && (
          <div className="border-t border-gray-200 bg-white lg:hidden">
            <div className="px-4 py-4">
              <nav className="space-y-1">
                {navItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => {
                      onNavigate(item.id);
                      setShowMobileMenu(false);
                    }}
                    className={`flex w-full items-center px-3 py-2 text-left text-sm font-medium transition-colors ${
                      currentPage === item.id
                        ? "text-primary-purple"
                        : "text-gray-700 hover:text-gray-900"
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
              </nav>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
