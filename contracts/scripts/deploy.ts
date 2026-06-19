import { ethers } from "hardhat";

async function main() {
  const [deployer] = await ethers.getSigners();
  const admin = process.env.ADMIN_ADDRESS || deployer.address;
  const oracle = process.env.ORACLE_ADDRESS;
  const pauser = process.env.PAUSER_ADDRESS || admin;

  if (!oracle) {
    throw new Error("ORACLE_ADDRESS is required");
  }

  const Token = await ethers.getContractFactory("DriverToken");
  const token = await Token.deploy(admin, oracle, pauser);
  await token.waitForDeployment();

  console.log(`DriverToken deployed to ${await token.getAddress()}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
