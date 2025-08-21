// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract FraudDetection {
    event FraudAlert(address indexed triggeredBy, string reason, uint256 timestamp, bytes32 requestId);

    // no storage, no constructor — nothing that can revert
    function triggerAlert(string memory reason, bytes32 requestId) external {
        emit FraudAlert(msg.sender, reason, block.timestamp, requestId);
    }
}
