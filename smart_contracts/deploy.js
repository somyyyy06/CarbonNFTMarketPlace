
const { ethers } = require("hardhat");

async function main() {
    console.log("Deploying CarbonNFT contract...");
    
    const CarbonNFT = await ethers.getContractFactory("CarbonNFT");
    const carbonNFT = await CarbonNFT.deploy();
    
    await carbonNFT.deployed();
    
    console.log("CarbonNFT deployed to:", carbonNFT.address);
    console.log("Transaction hash:", carbonNFT.deployTransaction.hash);
    
    // Verify contract on Polygonscan (optional)
    if (network.name !== "hardhat" && network.name !== "localhost") {
        console.log("Waiting for block confirmations...");
        await carbonNFT.deployTransaction.wait(6);
        
        console.log("Verifying contract...");
        try {
            await hre.run("verify:verify", {
                address: carbonNFT.address,
                constructorArguments: [],
            });
        } catch (e) {
            console.log("Verification failed:", e.message);
        }
    }
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
