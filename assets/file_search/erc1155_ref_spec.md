```solidity

pragma solidity >= 0.5.0;

contract ERC1155 {
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

    /**
     * @dev See {IERC1155-balanceOf}.
     *
     * Requirements:
     *
     * - `account` cannot be the zero address.
     */

    /// @notice postcondition _balances[_id][_owner] == balance
    function balanceOf(address _owner, uint256 _id) public view   returns (uint256 balance);

    /**
     * @dev See {IERC1155-balanceOfBatch}.
     *
     * Requirements:
     *
     * - `accounts` and `ids` must have the same length.
     */
    /// @notice postcondition batchBalances.length == _owners.length
    /// @notice postcondition batchBalances.length == _ids.length
    /// @notice postcondition forall (uint x) !( 0 <= x &&  x < batchBalances.length ) || batchBalances[x] == _balances[_ids[x]][_owners[x]]
    function balanceOfBatch(address[] memory _owners, uint256[] memory _ids) public view returns (uint256[] memory batchBalances);

    /**
     * @dev See {IERC1155-setApprovalForAll}.
     */

    /// @notice postcondition _operatorApprovals[msg.sender][_operator] == _approved
    function setApprovalForAll(address _operator, bool _approved) public;

    ///@notice postcondition _operatorApprovals[_owner][_operator] == approved
    function isApprovedForAll(address _owner, address _operator) public view returns (bool approved);


    /// @notice postcondition _to != address(0)
    /// @notice postcondition _operatorApprovals[_from][msg.sender] || _from == msg.sender
    /// @notice postcondition __verifier_old_uint(_balances[_id][_from]) >= _value    
    /// @notice postcondition _from == _to || _balances[_id][_from] == __verifier_old_uint(_balances[_id][_from]) - _value
    /// @notice postcondition _from != _to || _balances[_id][_from] == __verifier_old_uint(_balances[_id][_from])
    /// @notice postcondition _from == _to || _balances[_id][_to] == __verifier_old_uint(_balances[_id][_to]) + _value
    /// @notice postcondition _from != _to || _balances[_id][_to] == __verifier_old_uint(_balances[_id][_to])
    function safeTransferFrom(address _from, address _to, uint256 _id, uint256 _value, bytes memory _data) public;

    /// @notice postcondition _operatorApprovals[_from][msg.sender] || _from == msg.sender
    /// @notice postcondition _to != address(0)
    /// @notice postcondition _ids.length == _values.length
    /// @notice postcondition forall (uint x) !(0 <= x && x < _ids.length) || (__verifier_old_uint(_balances[_ids[x]][_from]) >= _values[x])
    /// @notice postcondition forall (uint x) !(0 <= x && x < _ids.length) || (_from == _to) || (_balances[_ids[x]][_to] == __verifier_old_uint(_balances[_ids[x]][_to]) + _values[x])
    /// @notice postcondition forall (uint x) _from != _to || _balances[_ids[x]][_to] == __verifier_old_uint(_balances[_ids[x]][_to])
    /// @notice postcondition forall (uint x) !(0 <= x && x < _ids.length) || (_from == _to) || ( _balances[_ids[x]][_from] == __verifier_old_uint(_balances[_ids[x]][_from]) - _values[x])
    /// @notice postcondition forall (uint x) _from != _to || _balances[_ids[x]][_from] == __verifier_old_uint(_balances[_ids[x]][_from])
    function safeBatchTransferFrom(address _from, address _to, uint256[] memory _ids, uint256[] memory _values) public;
}
```