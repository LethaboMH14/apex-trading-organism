require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  networks: {
    hardhat: {},
    sepolia: {
      url: "https://sepolia.base.org",
      chainId: 84532,
      gasPrice: 2000000000,
      accounts: process.env.APEX_PRIVATE_KEY ? [process.env.APEX_PRIVATE_KEY] : []
    }
  }
};
