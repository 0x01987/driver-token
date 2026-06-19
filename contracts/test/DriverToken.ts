import { expect } from "chai";
import { ethers } from "hardhat";

describe("DriverToken", function () {
  async function signClaim(token: any, oracle: any, driver: string, rideHash: string, amount: bigint | number, nonce: number) {
    const chainId = Number((await ethers.provider.getNetwork()).chainId);
    return oracle.signTypedData(
      {
        name: "DriverToken",
        version: "1",
        chainId,
        verifyingContract: await token.getAddress()
      },
      {
        Claim: [
          { name: "driver", type: "address" },
          { name: "rideHash", type: "bytes32" },
          { name: "amount", type: "uint256" },
          { name: "nonce", type: "uint256" }
        ]
      },
      {
        driver,
        rideHash,
        amount,
        nonce
      }
    );
  }

  it("mints once for a valid oracle-signed ride claim", async function () {
    const [admin, oracle, driver, pauser] = await ethers.getSigners();
    const Token = await ethers.getContractFactory("DriverToken");
    const token = await Token.deploy(admin.address, oracle.address, pauser.address);

    const rideHash = ethers.id("uber:ride-1");
    const amount = 10;
    const nonce = 0;
    const signature = await signClaim(token, oracle, driver.address, rideHash, amount, nonce);

    await expect(token.connect(driver).claim(rideHash, amount, nonce, signature))
      .to.emit(token, "Claimed")
      .withArgs(driver.address, rideHash, amount, nonce);

    await expect(token.connect(driver).claim(rideHash, amount, nonce, signature)).to.be.revertedWith(
      "ride already claimed"
    );
  });

  it("rejects claims above the 100 million token cap", async function () {
    const [admin, oracle, driver, pauser] = await ethers.getSigners();
    const Token = await ethers.getContractFactory("DriverToken");
    const token = await Token.deploy(admin.address, oracle.address, pauser.address);

    expect(await token.MAX_SUPPLY()).to.equal(ethers.parseEther("100000000"));

    const rideHash = ethers.id("uber:too-large");
    const amount = 100_000_001n;
    const signature = await signClaim(token, oracle, driver.address, rideHash, amount, 0);

    await expect(token.connect(driver).claim(rideHash, amount, 0, signature)).to.be.revertedWith(
      "max supply exceeded"
    );
  });
});
