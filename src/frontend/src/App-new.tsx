import { useState, useEffect } from "react";
import { AuthService, type AuthState } from "./services/auth";
import { BackendService } from "./services/backend";

// Debug component to test wallet connections
function WalletDebug() {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    principal: null,
    identity: null,
  });
  const [debugInfo, setDebugInfo] = useState<any>({});
  const [backendStatus, setBackendStatus] = useState<string>("Untested");

  useEffect(() => {
    // Initialize auth state
    AuthService.getAuthState().then(setAuthState);

    // Listen for auth changes
    AuthService.addAuthListener(setAuthState);

    // Get debug info
    setDebugInfo({
      canisterId: process.env.CANISTER_ID_BACKEND,
      dfxNetwork: process.env.DFX_NETWORK,
      nodeEnv: process.env.NODE_ENV,
      hasPlug: !!(window as any).ic?.plug,
      hasStoic: !!(window as any).ic?.stoicConnect,
      allEnvVars: {
        CANISTER_ID_BACKEND: process.env.CANISTER_ID_BACKEND,
        CANISTER_ID_FRONTEND: process.env.CANISTER_ID_FRONTEND,
        DFX_NETWORK: process.env.DFX_NETWORK,
        NODE_ENV: process.env.NODE_ENV,
      },
    });

    return () => {
      AuthService.removeAuthListener(setAuthState);
    };
  }, []);

  const handleWalletConnect = async (walletType: "plug" | "stoic") => {
    console.log(`Attempting to connect ${walletType} wallet...`);
    const success = await AuthService.connectWallet(walletType);
    console.log(`${walletType} connection result:`, success);

    if (success) {
      // Test backend connection after successful wallet connection
      setBackendStatus("Testing...");
      const backendConnected = await BackendService.testConnection();
      setBackendStatus(backendConnected ? "Connected" : "Failed");
    }
  };

  const handleLogin = async () => {
    console.log("Attempting Internet Identity login...");
    const success = await AuthService.login();
    console.log("Internet Identity login result:", success);
  };

  const handleLogout = async () => {
    await AuthService.logout();
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="mx-auto max-w-4xl">
        <h1 className="mb-8 text-3xl font-bold">Wallet Connection Debug</h1>

        {/* Debug Information */}
        <div className="mb-8 rounded-lg bg-white p-6 shadow">
          <h2 className="mb-4 text-xl font-semibold">Environment Debug Info</h2>
          <pre className="rounded bg-gray-100 p-4 text-sm">
            {JSON.stringify(debugInfo, null, 2)}
          </pre>
        </div>

        {/* Auth State */}
        <div className="mb-8 rounded-lg bg-white p-6 shadow">
          <h2 className="mb-4 text-xl font-semibold">Current Auth State</h2>
          <div className="space-y-2">
            <p>
              <strong>Authenticated:</strong>{" "}
              {authState.isAuthenticated ? "Yes" : "No"}
            </p>
            <p>
              <strong>Principal:</strong>{" "}
              {authState.principal?.toString() || "None"}
            </p>
            <p>
              <strong>Identity:</strong>{" "}
              {authState.identity ? "Present" : "None"}
            </p>
            <p>
              <strong>Backend Status:</strong>{" "}
              <span
                className={`font-semibold ${
                  backendStatus === "Connected"
                    ? "text-green-600"
                    : backendStatus === "Failed"
                      ? "text-red-600"
                      : backendStatus === "Testing..."
                        ? "text-yellow-600"
                        : "text-gray-600"
                }`}
              >
                {backendStatus}
              </span>
            </p>
          </div>
        </div>

        {/* Wallet Connection Buttons */}
        <div className="mb-8 rounded-lg bg-white p-6 shadow">
          <h2 className="mb-4 text-xl font-semibold">Wallet Connections</h2>

          {!authState.isAuthenticated ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                <button
                  onClick={() => handleWalletConnect("plug")}
                  className="rounded bg-blue-500 px-6 py-3 font-bold text-white hover:bg-blue-700"
                  disabled={!debugInfo.hasPlug}
                >
                  Connect Plug Wallet
                  {!debugInfo.hasPlug && " (Not Installed)"}
                </button>

                <button
                  onClick={() => handleWalletConnect("stoic")}
                  className="rounded bg-green-500 px-6 py-3 font-bold text-white hover:bg-green-700"
                  disabled={!debugInfo.hasStoic}
                >
                  Connect Stoic Wallet
                  {!debugInfo.hasStoic && " (Not Installed)"}
                </button>

                <button
                  onClick={handleLogin}
                  className="rounded bg-purple-500 px-6 py-3 font-bold text-white hover:bg-purple-700"
                >
                  Internet Identity
                </button>
              </div>

              <div className="mt-4 rounded bg-yellow-100 p-4">
                <h3 className="font-semibold">Instructions:</h3>
                <ul className="mt-2 list-inside list-disc space-y-1">
                  <li>
                    Pour utiliser Plug Wallet: Installez l'extension depuis{" "}
                    <a
                      href="https://plugwallet.ooo/"
                      className="text-blue-600 underline"
                    >
                      plugwallet.ooo
                    </a>
                  </li>
                  <li>
                    Pour utiliser Stoic Wallet: Installez l'extension depuis{" "}
                    <a
                      href="https://www.stoicwallet.com/"
                      className="text-blue-600 underline"
                    >
                      stoicwallet.com
                    </a>
                  </li>
                  <li>
                    En développement local, Internet Identity n'est pas
                    disponible
                  </li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="rounded bg-green-100 p-4">
                <p className="text-green-800">✅ Connecté avec succès!</p>
                <p>Principal: {authState.principal?.toString()}</p>
              </div>
              <button
                onClick={handleLogout}
                className="rounded bg-red-500 px-4 py-2 font-bold text-white hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          )}
        </div>

        {/* Console Logs */}
        <div className="rounded-lg bg-white p-6 shadow">
          <h2 className="mb-4 text-xl font-semibold">Debug Instructions</h2>
          <p className="text-gray-600">
            Ouvrez la console du navigateur (F12) pour voir les logs détaillés
            des tentatives de connexion.
          </p>
        </div>
      </div>
    </div>
  );
}

export default WalletDebug;
