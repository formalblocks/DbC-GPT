// Added by Pedro: Extracted from: https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/19c74140523e9af5a8489fe484456ca2adc87484/contracts/token/ERC20/IERC20.sol

// Version modified to work with solc-0.7 family
pragma solidity >=0.5.7;

/**
 * @title ERC20 interface
 * @dev see https://eips.ethereum.org/EIPS/eip-20
 */
interface IERC20 {
    function transfer(address to, uint256 value) external returns (bool);

    function approve(address spender, uint256 value) external returns (bool);

    function transferFrom(address from, address to, uint256 value) external returns (bool);

    function totalSupply() external view returns (uint256);

    function balanceOf(address who) external view returns (uint256);

    function allowance(address owner, address spender) external view returns (uint256);

    event Transfer(address indexed from, address indexed to, uint256 value);

    event Approval(address indexed owner, address indexed spender, uint256 value);
}