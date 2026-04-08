const { ethers } = require("hardhat");

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

async function main() {
  console.log("🚀 Deploying APEX contracts to Base Sepolia...");
  
  // Get the deployer account
  const [deployer] = await ethers.getSigners();
  console.log("📛 Deploying contracts with account:", deployer.address);
  
  // Check account balance
  const balance = await deployer.provider.getBalance(deployer.address);
  console.log("💰 Account balance:", balance.toString() + " wei");
  
  if (balance.toString() === "0") {
    console.error("❌ Account has no balance - using test deployment");
    console.log("📝 This is a mock deployment for demonstration");
  }
  
  // Deploy IdentityRegistry
  console.log("\n🏛️ Deploying IdentityRegistry...");
  const IdentityRegistry = await ethers.getContractFactory("IdentityRegistry");
  const identityRegistry = await IdentityRegistry.deploy();
  await identityRegistry.waitForDeployment();
  console.log("✅ IdentityRegistry deployed to:", await identityRegistry.target);
  await sleep(5000);
  
  // Deploy ReputationRegistry
  console.log("\n⭐ Deploying ReputationRegistry...");
  const ReputationRegistry = await ethers.getContractFactory("ReputationRegistry");
  const reputationRegistry = await ReputationRegistry.deploy();
  await reputationRegistry.waitForDeployment();
  console.log("✅ ReputationRegistry deployed to:", await reputationRegistry.target);
  await sleep(5000);
  
  // Deploy ValidationRegistry
  console.log("\n🔍 Deploying ValidationRegistry...");
  const ValidationRegistry = await ethers.getContractFactory("ValidationRegistry");
  const validationRegistry = await ValidationRegistry.deploy();
  await validationRegistry.waitForDeployment();
  console.log("✅ ValidationRegistry deployed to:", await validationRegistry.target);
  await sleep(5000);
  
  // Authorize deployer in ReputationRegistry
  console.log("\n🔐 Setting up authorizations...");
  await reputationRegistry.setAuthorizedCaller(deployer.address, true);
  console.log("✅ Deployer authorized in ReputationRegistry");
  
  // Authorize deployer in ValidationRegistry
  await validationRegistry.setAuthorizedValidator(deployer.address, true);
  console.log("✅ Deployer authorized in ValidationRegistry");
  
  // Mint a test agent NFT - commented out to prevent execution reverted error
  // NFT will be minted when apex-identity.py runs for the first time
  /*
  console.log("\n🏷️ Minting test agent NFT...");
  const testCardURI = "https://gateway.pinata.cloud/ipfs/QmTest123"; // Mock IPFS URI
  await identityRegistry.mintAgentNFT(deployer.address, testCardURI);
  console.log("✅ Test agent NFT minted");
  */
  
  // Display deployment summary
  console.log("\n" + "=".repeat(60));
  console.log("🎉 APEX CONTRACT DEPLOYMENT COMPLETE");
  console.log("=".repeat(60));
  console.log("📋 Contract Addresses:");
  console.log("🏛️  IdentityRegistry:", await identityRegistry.target);
  console.log("⭐  ReputationRegistry:", await reputationRegistry.target);
  console.log("🔍  ValidationRegistry:", await validationRegistry.target);
  console.log("📛  Deployer:", deployer.address);
  console.log("🌐  Network: Base Sepolia (Chain ID: 84532)");
  
  // Generate .env entries
  console.log("\n📝 Add these to your .env file:");
  console.log("IDENTITY_REGISTRY_ADDRESS=" + await identityRegistry.target);
  console.log("REPUTATION_REGISTRY_ADDRESS=" + await reputationRegistry.target);
  console.log("VALIDATION_REGISTRY_ADDRESS=" + await validationRegistry.target);
  
  console.log("\n🔗 Verify on BaseScan:");
  console.log("https://sepolia.basescan.org/address/" + await identityRegistry.target);
  console.log("https://sepolia.basescan.org/address/" + await reputationRegistry.target);
  console.log("https://sepolia.basescan.org/address/" + await validationRegistry.target);
  
  console.log("\n🚀 APEX is ready for on-chain operations!");
}

// Handle errors
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("💥 Deployment failed:", error);
    process.exit(1);
  });
