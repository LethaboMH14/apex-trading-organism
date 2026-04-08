const { ethers } = require("hardhat");

async function main() {
  console.log("🚀 Deploying APEX contracts to Base Sepolia...");
  
  // Get the deployer account
  const [deployer] = await ethers.getSigners();
  console.log("📛 Deploying contracts with account:", deployer.address);
  
  // Check account balance
  const balance = await deployer.provider.getBalance(deployer.address);
  console.log("💰 Account balance:", ethers.utils.formatEther(balance), "ETH");
  
  // Deploy IdentityRegistry
  console.log("\n🏛️ Deploying IdentityRegistry...");
  const IdentityRegistry = await ethers.getContractFactory("IdentityRegistry");
  const identityRegistry = await IdentityRegistry.deploy();
  await identityRegistry.deployed();
  console.log("✅ IdentityRegistry deployed to:", identityRegistry.address);
  
  // Deploy ReputationRegistry
  console.log("\n⭐ Deploying ReputationRegistry...");
  const ReputationRegistry = await ethers.getContractFactory("ReputationRegistry");
  const reputationRegistry = await ReputationRegistry.deploy();
  await reputationRegistry.deployed();
  console.log("✅ ReputationRegistry deployed to:", reputationRegistry.address);
  
  // Deploy ValidationRegistry
  console.log("\n🔍 Deploying ValidationRegistry...");
  const ValidationRegistry = await ethers.getContractFactory("ValidationRegistry");
  const validationRegistry = await ValidationRegistry.deploy();
  await validationRegistry.deployed();
  console.log("✅ ValidationRegistry deployed to:", validationRegistry.address);
  
  // Display deployment summary
  console.log("\n" + "=".repeat(60));
  console.log("🎉 APEX CONTRACT DEPLOYMENT COMPLETE");
  console.log("=".repeat(60));
  console.log("📋 Contract Addresses:");
  console.log("🏛️  IdentityRegistry:", identityRegistry.address);
  console.log("⭐  ReputationRegistry:", reputationRegistry.address);
  console.log("🔍  ValidationRegistry:", validationRegistry.address);
  console.log("📛  Deployer:", deployer.address);
  console.log("🌐  Network: Base Sepolia (Chain ID: 84532)");
  
  // Generate .env entries
  console.log("\n📝 Add these to your .env file:");
  console.log("IDENTITY_REGISTRY_ADDRESS=" + identityRegistry.address);
  console.log("REPUTATION_REGISTRY_ADDRESS=" + reputationRegistry.address);
  console.log("VALIDATION_REGISTRY_ADDRESS=" + validationRegistry.address);
  
  console.log("\n🔗 Verify on BaseScan:");
  console.log("https://sepolia.basescan.org/address/" + identityRegistry.address);
  console.log("https://sepolia.basescan.org/address/" + reputationRegistry.address);
  console.log("https://sepolia.basescan.org/address/" + validationRegistry.address);
  
  console.log("\n🚀 APEX is ready for on-chain operations!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("💥 Deployment failed:", error);
    process.exit(1);
  });
