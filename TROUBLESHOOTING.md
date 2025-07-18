# Troubleshooting Guide

## Common Issues and Solutions

### 1. "Call failed: Canister has no query method"

**Problem**: The frontend can't connect to backend methods.

**Solution**:

```bash
# Rebuild and redeploy the backend canister
dfx build backend
dfx deploy backend
```

### 2. Frontend won't start or shows blank page

**Problem**: Development server issues or build errors.

**Solution**:

```bash
# Clear node modules and reinstall
cd src/frontend
rm -rf node_modules package-lock.json
npm install

# Start development server
npm start
```

### 3. IC replica not running

**Problem**: dfx commands fail with connection errors.

**Solution**:

```bash
# Start the IC replica
dfx start --background

# Or start in foreground to see logs
dfx start
```

### 4. Wallet connection fails

**Problem**: Internet Identity or wallet plugins don't work.

**Solution**:

- Make sure you're using a supported browser (Chrome, Firefox)
- Install Plug wallet extension if using Plug
- Try Internet Identity authentication instead
- Check browser console for errors

### 5. Type errors in development

**Problem**: TypeScript compilation errors.

**Solution**:

```bash
# Regenerate type declarations
dfx generate

# Check for type errors
cd src/frontend
npx tsc --noEmit
```

### 6. Candid interface doesn't match

**Problem**: Frontend types don't match backend.

**Solution**:

```bash
# Regenerate candid and types
npm run generate-candid
cd src/frontend && npm run build
```

### 7. Markets don't load or show old data

**Problem**: Backend state issues or old canister data.

**Solution**:

```bash
# Reset local development environment
dfx stop
dfx start --clean --background
dfx deploy
```

## Development Commands

### Quick Reset (Nuclear Option)

```bash
# Stop everything
dfx stop

# Clean all local state
dfx start --clean --background

# Rebuild everything
npm run build

# Deploy all canisters
dfx deploy

# Start frontend
cd src/frontend && npm start
```

### Check System Status

```bash
# Check IC replica
dfx ping

# Check canister status
dfx canister status backend

# Check frontend build
cd src/frontend && npm run build
```

### Logs and Debugging

```bash
# View IC replica logs
dfx start  # (without --background)

# View backend canister logs
dfx logs backend

# View frontend development logs
cd src/frontend && npm start  # check terminal output
```

## Need Help?

1. Check the browser console for JavaScript errors
2. Check the terminal for build/deployment errors
3. Verify all dependencies are installed
4. Make sure you're using compatible Node.js version (16+)
5. Try the "Quick Reset" commands above
