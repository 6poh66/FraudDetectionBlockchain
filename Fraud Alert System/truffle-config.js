module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",
      port: 7545,        // use 8545 if your Ganache CLI runs there
      network_id: "*",
    },
  },
  compilers: {
    solc: {
      version: "0.8.20",   // pin to 0.8.20 for Ganache London hardfork
      settings: {
        optimizer: { enabled: true, runs: 200 },
        evmVersion: "london"
      }
    }
  }
};

