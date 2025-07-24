export function ModernFooter() {
  return (
    <footer className="bg-gradient-icp-footer text-white">
      <div className="container-portugal py-12 sm:py-16 lg:py-20">
        <div className="grid grid-cols-1 gap-8 sm:gap-12 md:grid-cols-2 lg:grid-cols-4">
          {/* Brand Section - Portugal Style avec couleur ICP */}
          <div className="space-y-4 sm:space-y-6 lg:col-span-1">
            <div className="flex items-center space-x-3 sm:space-x-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/20 shadow-xl backdrop-blur-sm sm:h-12 sm:w-12">
                <span className="text-lg font-bold text-white sm:text-xl">
                  CP
                </span>
              </div>
              <div>
                <span className="text-xl font-bold text-white sm:text-2xl">
                  ChainPredict
                </span>
                <div className="text-base font-semibold text-blue-300 sm:text-lg">
                  ICP
                </div>
              </div>
            </div>

            <p className="text-lg leading-relaxed text-white/80">
              Accelerating the adoption of prediction markets on the Internet
              Computer Protocol and supporting builders through every stage of
              their journey.
            </p>

            <div className="flex space-x-4">
              {[
                { icon: "🔗", label: "LinkedIn", href: "#" },
                { icon: "𝕏", label: "Twitter", href: "#" },
                { icon: "📱", label: "Telegram", href: "#" },
                { icon: "💻", label: "GitHub", href: "#" },
              ].map((social) => (
                <a
                  key={social.label}
                  href={social.href}
                  className="group flex h-12 w-12 items-center justify-center rounded-xl bg-white/10 backdrop-blur-sm transition-all duration-300 hover:scale-105 hover:bg-white/20"
                  aria-label={social.label}
                >
                  <span className="text-xl transition-transform group-hover:scale-110">
                    {social.icon}
                  </span>
                </a>
              ))}
            </div>
          </div>

          {/* Markets */}
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-white">Markets</h3>
            <ul className="space-y-3">
              {[
                { name: "🔥 Trending", href: "#" },
                { name: "💻 Technology", href: "#" },
                { name: "₿ Cryptocurrency", href: "#" },
                { name: "💰 Finance", href: "#" },
                { name: "⚽ Sports", href: "#" },
                { name: "🗳️ Politics", href: "#" },
              ].map((item) => (
                <li key={item.name}>
                  <a
                    href={item.href}
                    className="inline-block transform text-white/70 transition-colors duration-200 hover:translate-x-1 hover:text-white"
                  >
                    {item.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources */}
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-white">Resources</h3>
            <ul className="space-y-3">
              {[
                { name: "📚 How it Works", href: "#" },
                { name: "📈 Trading Guide", href: "#" },
                { name: "🔧 API Docs", href: "#" },
                { name: "❓ FAQ", href: "#" },
                { name: "📝 Blog", href: "#" },
                { name: "🎓 Academy", href: "#" },
              ].map((item) => (
                <li key={item.name}>
                  <a
                    href={item.href}
                    className="inline-block transform text-white/70 transition-colors duration-200 hover:translate-x-1 hover:text-white"
                  >
                    {item.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal & Status */}
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-white">Legal & Status</h3>
            <ul className="space-y-3">
              {[
                { name: "📋 Terms of Service", href: "#" },
                { name: "🔒 Privacy Policy", href: "#" },
                { name: "⚠️ Risk Disclosure", href: "#" },
                { name: "📞 Contact", href: "#" },
              ].map((item) => (
                <li key={item.name}>
                  <a
                    href={item.href}
                    className="inline-block transform text-white/70 transition-colors duration-200 hover:translate-x-1 hover:text-white"
                  >
                    {item.name}
                  </a>
                </li>
              ))}
            </ul>

            {/* System Status */}
            <div className="glass-card rounded-lg border border-white/10 bg-white/5 p-4">
              <div className="mb-2 flex items-center space-x-2">
                <div className="h-2 w-2 animate-pulse rounded-full bg-green-400"></div>
                <span className="text-sm font-medium text-green-400">
                  All Systems Operational
                </span>
              </div>
              <div className="text-xs text-white/60">
                Network:{" "}
                {process.env.DFX_NETWORK === "local"
                  ? "🏗️ Local Dev"
                  : "🌐 Mainnet"}
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="mt-16 border-t border-white/20 pt-8">
          <div className="flex flex-col items-center justify-between space-y-4 lg:flex-row lg:space-y-0">
            <div className="flex items-center space-x-6 text-sm text-white/60">
              <span>© 2025 ChainPredict ICP</span>
              <span className="hidden sm:inline">•</span>
              <span className="hidden sm:inline">
                Powered by Internet Computer
              </span>
              <span className="hidden md:inline">•</span>
              <span className="hidden md:inline">Built with ❤️ for Web3</span>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-xs text-white/60">
                <svg
                  className="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
                <span>99.9% Uptime</span>
              </div>
              <span className="text-white/30">|</span>
              <div className="flex items-center space-x-2 text-xs text-white/60">
                <svg
                  className="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <span>Verified Smart Contracts</span>
              </div>
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="glass-card mt-8 rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <svg
                className="mt-0.5 h-5 w-5 text-yellow-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
                />
              </svg>
            </div>
            <div>
              <p className="text-xs leading-relaxed text-white/70">
                <strong className="text-yellow-400">Risk Disclaimer:</strong>{" "}
                Prediction markets involve financial risk. Past performance
                doesn't guarantee future results. Trade responsibly with funds
                you can afford to lose. ChainPredict ICP is a decentralized
                application on the Internet Computer blockchain. Users are
                solely responsible for their trading decisions.
              </p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
