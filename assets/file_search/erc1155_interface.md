// SPDX-License-Identifier: MIT

pragma solidity >= 0.5.0;

contract IERC1155  {

    event TransferSingle(address indexed operator, address indexed from, address indexed to, uint256 id, uint256 value);
    event TransferBatch(address indexed operator, address indexed from, address indexed to, uint256[] ids, uint256[] values);
    event ApprovalForAll(address indexed account, address indexed operator, bool approved);
    event URI(string value, uint256 indexed id);

    // Mapping from token ID to account balances
    mapping (uint256 => mapping(address => uint256)) private _balances;

    // Mapping from account to operator approvals
    mapping (address => mapping(address => bool)) private _operatorApprovals;

    // Used as the URI for all token types by relying on ID substitution, e.g. https://token-cdn-domain/{id}.json
    string private _uri;

    function balanceOf(address account, uint256 id) public view   returns (uint256 balance);
    
    function balanceOfBatch(address[] memory accounts, uint256[] memory ids) public view returns (uint256[] memory batchBalances);

    function setApprovalForAll(address operator, bool approved) public;

    function isApprovedForAll(address account, address operator) public view returns (bool approved);

    function safeTransferFrom(address from, address to, uint256 id, uint256 amount, bytes memory data) public;

    function safeBatchTransferFrom(address from, address to, uint256[] memory ids, uint256[] memory amounts, bytes memory data) public;
}