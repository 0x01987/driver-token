// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";

contract DriverToken is ERC20, AccessControl, Pausable, EIP712 {
    using ECDSA for bytes32;

    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant ORACLE_ROLE = keccak256("ORACLE_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant CLAIM_TYPEHASH =
        keccak256("Claim(address driver,bytes32 rideHash,uint256 amount,uint256 nonce)");
    uint256 public constant MAX_SUPPLY = 100_000_000 * 10 ** 18;

    mapping(bytes32 rideHash => bool used) public usedRideHashes;

    event Claimed(address indexed driver, bytes32 indexed rideHash, uint256 amount, uint256 nonce);

    constructor(address admin, address oracle, address pauser)
        ERC20("Driver Token", "DRIVE")
        EIP712("DriverToken", "1")
    {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(ADMIN_ROLE, admin);
        _grantRole(ORACLE_ROLE, oracle);
        _grantRole(PAUSER_ROLE, pauser);
    }

    function claim(bytes32 rideHash, uint256 amount, uint256 nonce, bytes calldata signature) external whenNotPaused {
        require(!usedRideHashes[rideHash], "ride already claimed");

        bytes32 digest = _hashTypedDataV4(keccak256(abi.encode(CLAIM_TYPEHASH, msg.sender, rideHash, amount, nonce)));
        address signer = digest.recover(signature);
        require(hasRole(ORACLE_ROLE, signer), "invalid oracle signature");

        uint256 mintAmount = amount * 10 ** decimals();
        require(totalSupply() + mintAmount <= MAX_SUPPLY, "max supply exceeded");

        usedRideHashes[rideHash] = true;
        _mint(msg.sender, mintAmount);

        emit Claimed(msg.sender, rideHash, amount, nonce);
    }

    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(ADMIN_ROLE) {
        _unpause();
    }
}
