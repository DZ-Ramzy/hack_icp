import { AuthClient } from "@dfinity/auth-client";
import { Principal } from "@dfinity/principal";

export interface AuthState {
  isAuthenticated: boolean;
  principal: Principal | null;
  identity: any | null;
}

export class AuthService {
  private static authClient: AuthClient | null = null;
  private static listeners: ((state: AuthState) => void)[] = [];
  private static walletConnection: {
    type: "plug" | "stoic" | "ii" | null;
    principal: Principal | null;
  } = { type: null, principal: null };

  static async init(): Promise<void> {
    if (!this.authClient) {
      this.authClient = await AuthClient.create();
    }
  }

  static async login(): Promise<boolean> {
    try {
      await this.init();

      // For local development, redirect to using wallets
      const isLocal =
        process.env.DFX_NETWORK === "local" ||
        process.env.NODE_ENV === "development";

      if (isLocal) {
        alert(
          "En mode développement local, veuillez utiliser Plug Wallet ou Stoic Wallet pour vous connecter.",
        );
        return false;
      }

      return new Promise((resolve) => {
        this.authClient!.login({
          identityProvider: "https://identity.ic0.app",
          onSuccess: () => {
            // Store II connection state
            this.walletConnection = { type: "ii", principal: null }; // Principal will be updated in getAuthState
            this.notifyListeners();
            resolve(true);
          },
          onError: (error) => {
            console.error("Login failed:", error);
            resolve(false);
          },
        });
      });
    } catch (error) {
      console.error("Login initialization failed:", error);
      return false;
    }
  }

  static async logout(): Promise<void> {
    try {
      await this.init();
      await this.authClient!.logout();

      // Reset wallet connection state
      this.walletConnection = { type: null, principal: null };

      this.notifyListeners();
    } catch (error) {
      console.error("Logout failed:", error);
    }
  }

  static async getAuthState(): Promise<AuthState> {
    await this.init();

    // Check for wallet connections first
    if (this.walletConnection.type && this.walletConnection.principal) {
      return {
        isAuthenticated: true,
        principal: this.walletConnection.principal,
        identity: null, // Wallets don't use the same identity system
      };
    }

    // Fallback to Internet Identity
    const isAuthenticated = await this.authClient!.isAuthenticated();
    const identity = isAuthenticated ? this.authClient!.getIdentity() : null;
    const principal = identity ? identity.getPrincipal() : null;

    return {
      isAuthenticated,
      principal,
      identity,
    };
  }

  static addAuthListener(callback: (state: AuthState) => void): void {
    this.listeners.push(callback);
  }

  static removeAuthListener(callback: (state: AuthState) => void): void {
    this.listeners = this.listeners.filter((listener) => listener !== callback);
  }

  private static async notifyListeners(): Promise<void> {
    const state = await this.getAuthState();
    this.listeners.forEach((listener) => listener(state));
  }

  static async connectWallet(
    walletType: "plug" | "stoic" = "plug",
  ): Promise<boolean> {
    if (walletType === "plug") {
      return this.connectPlug();
    } else {
      return this.connectStoic();
    }
  }

  private static async connectPlug(): Promise<boolean> {
    try {
      // Check if Plug is available
      if (!(window as any).ic?.plug) {
        alert(
          "Plug wallet is not installed. Please install it from https://plugwallet.ooo/",
        );
        return false;
      }

      const plug = (window as any).ic.plug;

      // Determine the host based on environment
      const isLocal =
        process.env.DFX_NETWORK === "local" ||
        process.env.NODE_ENV === "development";
      const host = isLocal
        ? "http://127.0.0.1:4943"
        : "https://mainnet.dfinity.network";

      // Request connection
      const connected = await plug.requestConnect({
        whitelist: [process.env.CANISTER_ID_BACKEND],
        host,
      });

      console.log("Plug connection request details:", {
        canisterId: process.env.CANISTER_ID_BACKEND,
        host,
        connected,
      });

      if (connected) {
        const principal = await plug.agent.getPrincipal();
        console.log(
          "Connected to Plug wallet with principal:",
          principal.toString(),
        );

        // Store wallet connection state
        this.walletConnection = {
          type: "plug",
          principal: principal,
        };

        this.notifyListeners();
        return true;
      }

      return false;
    } catch (error) {
      console.error("Failed to connect to Plug wallet:", error);
      return false;
    }
  }

  private static async connectStoic(): Promise<boolean> {
    try {
      // Check if StoicConnect is available
      if (!(window as any).ic?.stoicConnect) {
        alert(
          "Stoic wallet is not installed. Please install it from https://www.stoicwallet.com/",
        );
        return false;
      }

      const stoic = (window as any).ic.stoicConnect;

      const connected = await stoic.connect();

      if (connected) {
        const principal = await stoic.principal();
        console.log(
          "Connected to Stoic wallet with principal:",
          principal.toString(),
        );

        // Store wallet connection state
        this.walletConnection = {
          type: "stoic",
          principal: principal,
        };

        this.notifyListeners();
        return true;
      }

      return false;
    } catch (error) {
      console.error("Failed to connect to Stoic wallet:", error);
      return false;
    }
  }
}

// Extend window interface for wallet types
declare global {
  interface Window {
    ic?: {
      plug?: {
        requestConnect: (options: any) => Promise<boolean>;
        agent: {
          getPrincipal: () => Promise<Principal>;
        };
      };
      stoicConnect?: {
        connect: () => Promise<boolean>;
        principal: () => Promise<Principal>;
      };
    };
  }
}
