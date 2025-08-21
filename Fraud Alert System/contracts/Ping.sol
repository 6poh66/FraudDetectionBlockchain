// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Ping {
    event Pong(address indexed who, uint256 when);
    function ping() external { emit Pong(msg.sender, block.timestamp); }
}

