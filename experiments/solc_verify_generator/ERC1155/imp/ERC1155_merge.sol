// SPDX-License-Identifier: MIT

pragma solidity >= 0.5.0;

// pragma solidity ^0.8.0;

import "./IERC1155.sol";
import "./IERC1155Receiver.sol";
import "./IERC1155MetadataURI.sol";
import "./Address.sol";
import "./Context.sol";
import "./ERC165.sol";

/**
 *
 * @dev Implementation of the basic standard multi-token.
 * See https://eips.ethereum.org/EIPS/eip-1155
 * Originally based on code by Enjin: https://github.com/enjin/erc-1155
 *
 * _Available since v3.1._
 */
///@notice invariant forall (uint256 i) sums[i] == total_supplies[i]
contract ERC1155 is Context, ERC165, IERC1155, IERC1155MetadataURI {
    using Address for address;

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
     * @dev See {_setURI}.
     */
    constructor (string memory uri_) public {
        _setURI(uri_);
    }

    /**
     * @dev See {IERC165-supportsInterface}.
     */
    // function supportsInterface(bytes4 interfaceId) public view  (ERC165, IERC165) returns (bool) {
    //     return interfaceId == type(IERC1155).interfaceId
    //         || interfaceId == type(IERC1155MetadataURI).interfaceId
    //         || super.supportsInterface(interfaceId);
    // }

    /**
     * @dev See {IERC1155MetadataURI-uri}.
     *
     * This implementation returns the same URI for *all* token types. It relies
     * on the token type ID substitution mechanism
     * https://eips.ethereum.org/EIPS/eip-1155#metadata[defined in the EIP].
     *
     * Clients calling this function must replace the `\{id\}` substring with the
     * actual token type ID.
     */
    function uri(uint256) public view   returns (string memory) {
        return _uri;
    }

    /**
     * @dev See {IERC1155-balanceOf}.
     *
     * Requirements:
     *
     * - `account` cannot be the zero address.
     */
    ///@notice postcondition _balances[_id][_owner] == balance  
/// @notice postcondition _owner != address(0)

    function balanceOf(address _owner, uint256 _id) public view   returns (uint256 balance) {
        require(_owner != address(0), "ERC1155: balance query for the zero address");
        return _balances[_id][_owner];
    }

    /**
     * @dev See {IERC1155-balanceOfBatch}.
     *
     * Requirements:
     *
     * - `accounts` and `ids` must have the same length.
     */
    ///@notice postcondition batchBalances.length == _owners.length 
/// @notice postcondition batchBalances.length == _ids.length
/// @notice postcondition forall (uint x) !(0 <= x && x < batchBalances.length) || batchBalances[x] == _balances[_ids[x]][_owners[x]]

    function balanceOfBatch(
        address[] memory _owners,
        uint256[] memory _ids
    )
        public
        view
        returns (uint256[] memory batchBalances)
    {
        require(_owners.length == _ids.length, "ERC1155: _owners and _ids length mismatch");

        batchBalances = new uint256[](_owners.length);

        uint256 length = _owners.length;
        /// @notice invariant (batchBalances.length == _ids.length && batchBalances.length == _owners.length)
        /// @notice invariant (0 <= i && i <= _owners.length)
        /// @notice invariant (0 <= i && i <= _ids.length)
        /// @notice invariant forall(uint k)  _ids[k] == __verifier_old_uint(_ids[k])
        /// @notice invariant forall (uint j) !(0 <= j && j < i && j < _owners.length ) || batchBalances[j] == _balances[_ids[j]][_owners[j]]
        for (uint256 i = 0; i < length; ++i) {
            batchBalances[i] = _balances[_ids[i]][_owners[i]]; // Modified (extracted from balanceOf)
        }

        return batchBalances;
    }

    /**
     * @dev See {IERC1155-setApprovalForAll}.
     */
    ///@notice postcondition _operatorApprovals[msg.sender][_operator] == _approved 
/// @notice postcondition _operatorApprovals[msg.sender][_operator] == true || _operatorApprovals[msg.sender][_operator] == false

    function setApprovalForAll(address _operator, bool _approved) public   {
        require(_msgSender() != _operator, "ERC1155: setting approval status for self");

        _operatorApprovals[_msgSender()][_operator] = _approved;
        emit ApprovalForAll(_msgSender(), _operator, _approved);
    }

    ///@notice postcondition _operatorApprovals[_owner][_operator] == __verifier_old_bool(_operatorApprovals[_owner][_operator]) || (_owner == msg.sender && _owner == _operator)
/// @notice postcondition _owner != address(0)

    function isApprovedForAll(address _owner, address _operator) public view returns (bool approved) {
        return _operatorApprovals[_owner][_operator];
    }

    /// @notice precondition _from != msg.sender
    /// @notice precondition !_operatorApprovals[_from][msg.sender]
    ///@notice postcondition _to != address(0) 
/// @notice postcondition _operatorApprovals[_from][msg.sender] || _from == msg.sender
/// @notice postcondition __verifier_old_uint(_balances[_id][_from]) >= _value    
/// @notice postcondition _balances[_id][_from] == __verifier_old_uint(_balances[_id][_from]) - _value
/// @notice postcondition _balances[_id][_to] == __verifier_old_uint(_balances[_id][_to]) + _value

    function safeTransferFrom(
        address _from,
        address _to,
        uint256 _id,
        uint256 _value,
        bytes memory _data
    )
        public
        
        
    {
        require(
            _from == _msgSender() || isApprovedForAll(_from, _msgSender()),
            "ERC1155: caller is not owner nor approved"
        );
        _safeTransferFrom(_from, _to, _id, _value, _data);
    }

    
    mapping(uint256 => uint256) private total_supplies;
    // Ghost variable as before
    mapping(uint256 => uint256) private sums;
    
    // Comments here because solc-verify does not allow inline comments with pre/post.
    // Pre 1.   Sort of axiomatises _old_balances == old(_balances)
    // Pre 2.   ids need to be injective, otherwise expressing some of these conditions goes beyond what solc-verify can do.
    //          For instance, if two ids elements, say x and y, point to the same id, we have that _balances[_ids[x]][_from] = __verifier_old_uint(_balances[_ids[x]][_from]) - (_values[x] + _values[y])
    // Pos.     Postcondition for from, we need to create an analogous to "to".
    ///@notice precondition forall (uint i, uint j) !(_ids[i] == _ids[j]) ||  i == j
    ///@notice postcondition forall (uint i) !(0 <= i && i < _ids.length && _from != _to) || (_balances[_ids[i]][_to] == __verifier_old_uint(_balances[_ids[i]][_to]) + _values[i])
/// @notice postcondition forall (uint i) !(0 <= i && i < _ids.length && _from != _to) || (_balances[_ids[i]][_from] == __verifier_old_uint(_balances[_ids[i]][_from]) - _values[i])

    function safeBatchTransferFrom(
        address _from,
        address _to,
        uint256[] memory _ids,
        uint256[] memory _values,
        bytes memory _data
    ) public /*virtual override*/{
        require(
            _from == msg.sender || _operatorApprovals[_from][msg.sender],
            "ERC1155: caller is not token owner or approved"
        );

        require(_ids.length == _values.length, "ERC1155: ids and amounts length mismatch");
        require(_to != address(0), "ERC1155: transfer to the zero address");

        address operator = msg.sender;
        ///@notice invariant forall (uint256 i) sums[i] == total_supplies[i]
        ///@notice invariant forall (uint j) !(0 <= j && j < i && _from != _to) || (_balances[_ids[j]][_from] == __verifier_old_uint(_balances[_ids[j]][_from]) - _values[j])
        ///@notice invariant forall (uint j) !(0 <= j && j < i && _from != _to) || (_balances[_ids[j]][_to] == __verifier_old_uint(_balances[_ids[j]][_to]) + _values[j])
        ///@notice invariant forall (uint j) !(0 <= j && j < i && _from == _to) || (_balances[_ids[j]][_to] == __verifier_old_uint(_balances[_ids[j]][_to]))
        ///@notice invariant forall (uint j) !(0 <= j && j < i && _from == _to) || (_balances[_ids[j]][_from] == __verifier_old_uint(_balances[_ids[j]][_from]))
        ///@notice invariant forall (uint j) !(0 > j || j >= i) || (_balances[_ids[j]][_from] == __verifier_old_uint(_balances[_ids[j]][_from]))
        ///@notice invariant forall (uint j) !(0 > j || j >= i) || (_balances[_ids[j]][_to] == __verifier_old_uint(_balances[_ids[j]][_to]))
        for (uint256 i = 0; i < _ids.length; ++i) {
            uint256 id = _ids[i];
            uint256 amount = _values[i];
  
            // Remove string from this requires as it changes the mem_arr
            //require(_balances[id][from] >= amount);
             
            sums[id] = sums[id] - _balances[id][_from];
            _balances[id][_from]= _balances[id][_from] - amount;
            sums[id] = sums[id] + _balances[id][_from];

            sums[id] = sums[id] - _balances[id][_to]; 
            _balances[id][_to] = _balances[id][_to] + amount;
            sums[id] = sums[id] + _balances[id][_to]; 
       }
    }  

    /**
     * @dev Transfers `amount` tokens of token type `id` from `from` to `to`.
     *
     * Emits a {TransferSingle} event.
     *
     * Requirements:
     *
     * - `to` cannot be the zero address.
     * - `from` must have a balance of tokens of type `id` of at least `amount`.
     * - If `to` refers to a smart contract, it must implement {IERC1155Receiver-onERC1155Received} and return the
     * acceptance magic value.
     */
    function _safeTransferFrom(
        address from,
        address to,
        uint256 id,
        uint256 amount,
        bytes memory data
    )
        internal
        
    {
        require(to != address(0), "ERC1155: transfer to the zero address");

        address operator = _msgSender();

        _beforeTokenTransfer(operator, from, to, _asSingletonArray(id), _asSingletonArray(amount), data);

        uint256 fromBalance = _balances[id][from];
        require(fromBalance >= amount, "ERC1155: insufficient balance for transfer");
        _balances[id][from] = fromBalance - amount;
        _balances[id][to] += amount;

        emit TransferSingle(operator, from, to, id, amount);

        _doSafeTransferAcceptanceCheck(operator, from, to, id, amount, data);
    }


    /**
     * @dev Sets a new URI for all token types, by relying on the token type ID
     * substitution mechanism
     * https://eips.ethereum.org/EIPS/eip-1155#metadata[defined in the EIP].
     *
     * By this mechanism, any occurrence of the `\{id\}` substring in either the
     * URI or any of the amounts in the JSON file at said URI will be replaced by
     * clients with the token type ID.
     *
     * For example, the `https://token-cdn-domain/\{id\}.json` URI would be
     * interpreted by clients as
     * `https://token-cdn-domain/000000000000000000000000000000000000000000000000000000000004cce0.json`
     * for token type ID 0x4cce0.
     *
     * See {uri}.
     *
     * Because these URIs cannot be meaningfully represented by the {URI} event,
     * this function emits no events.
     */
    function _setURI(string memory newuri) internal  {
        _uri = newuri;
    }

    /**
     * @dev Creates `amount` tokens of token type `id`, and assigns them to `account`.
     *
     * Emits a {TransferSingle} event.
     *
     * Requirements:
     *
     * - `account` cannot be the zero address.
     * - If `account` refers to a smart contract, it must implement {IERC1155Receiver-onERC1155Received} and return the
     * acceptance magic value.
     */
    function _mint(address account, uint256 id, uint256 amount, bytes memory data) internal  {
        require(account != address(0), "ERC1155: mint to the zero address");

        address operator = _msgSender();

        _beforeTokenTransfer(operator, address(0), account, _asSingletonArray(id), _asSingletonArray(amount), data);

        _balances[id][account] += amount;
        emit TransferSingle(operator, address(0), account, id, amount);

        _doSafeTransferAcceptanceCheck(operator, address(0), account, id, amount, data);
    }

    /**
     * @dev xref:ROOT:erc1155.adoc#batch-operations[Batched] version of {_mint}.
     *
     * Requirements:
     *
     * - `ids` and `amounts` must have the same length.
     * - If `to` refers to a smart contract, it must implement {IERC1155Receiver-onERC1155BatchReceived} and return the
     * acceptance magic value.
     */
    function _mintBatch(address to, uint256[] memory ids, uint256[] memory amounts, bytes memory data) internal  {
        require(to != address(0), "ERC1155: mint to the zero address");
        require(ids.length == amounts.length, "ERC1155: ids and amounts length mismatch");

        address operator = _msgSender();

        _beforeTokenTransfer(operator, address(0), to, ids, amounts, data);

        for (uint i = 0; i < ids.length; i++) {
            _balances[ids[i]][to] += amounts[i];
        }

        emit TransferBatch(operator, address(0), to, ids, amounts);

        _doSafeBatchTransferAcceptanceCheck(operator, address(0), to, ids, amounts, data);
    }

    /**
     * @dev Destroys `amount` tokens of token type `id` from `account`
     *
     * Requirements:
     *
     * - `account` cannot be the zero address.
     * - `account` must have at least `amount` tokens of token type `id`.
     */
    function _burn(address account, uint256 id, uint256 amount) internal  {
        require(account != address(0), "ERC1155: burn from the zero address");

        address operator = _msgSender();

        _beforeTokenTransfer(operator, account, address(0), _asSingletonArray(id), _asSingletonArray(amount), "");

        uint256 accountBalance = _balances[id][account];
        require(accountBalance >= amount, "ERC1155: burn amount exceeds balance");
        _balances[id][account] = accountBalance - amount;

        emit TransferSingle(operator, account, address(0), id, amount);
    }

    /**
     * @dev xref:ROOT:erc1155.adoc#batch-operations[Batched] version of {_burn}.
     *
     * Requirements:
     *
     * - `ids` and `amounts` must have the same length.
     */
    function _burnBatch(address account, uint256[] memory ids, uint256[] memory amounts) internal  {
        require(account != address(0), "ERC1155: burn from the zero address");
        require(ids.length == amounts.length, "ERC1155: ids and amounts length mismatch");

        address operator = _msgSender();

        _beforeTokenTransfer(operator, account, address(0), ids, amounts, "");

        for (uint i = 0; i < ids.length; i++) {
            uint256 id = ids[i];
            uint256 amount = amounts[i];

            uint256 accountBalance = _balances[id][account];
            require(accountBalance >= amount, "ERC1155: burn amount exceeds balance");
            _balances[id][account] = accountBalance - amount;
        }

        emit TransferBatch(operator, account, address(0), ids, amounts);
    }

    /**
     * @dev Hook that is called before any token transfer. This includes minting
     * and burning, as well as batched variants.
     *
     * The same hook is called on both single and batched variants. For single
     * transfers, the length of the `id` and `amount` arrays will be 1.
     *
     * Calling conditions (for each `id` and `amount` pair):
     *
     * - When `from` and `to` are both non-zero, `amount` of ``from``'s tokens
     * of token type `id` will be  transferred to `to`.
     * - When `from` is zero, `amount` tokens of token type `id` will be minted
     * for `to`.
     * - when `to` is zero, `amount` of ``from``'s tokens of token type `id`
     * will be burned.
     * - `from` and `to` are never both zero.
     * - `ids` and `amounts` have the same, non-zero length.
     *
     * To learn more about hooks, head to xref:ROOT:extending-contracts.adoc#using-hooks[Using Hooks].
     */
    function _beforeTokenTransfer(
        address operator,
        address from,
        address to,
        uint256[] memory ids,
        uint256[] memory amounts,
        bytes memory data
    )
        internal
        
    { }

    function _doSafeTransferAcceptanceCheck(
        address operator,
        address from,
        address to,
        uint256 id,
        uint256 amount,
        bytes memory data
    )
        private
    {
        if (to.isContract()) {
            // try IERC1155Receiver(to).onERC1155Received(operator, from, id, amount, data) returns (bytes4 response) {
            //     if (response != IERC1155Receiver(to).onERC1155Received.selector) {
            //         revert("ERC1155: ERC1155Receiver rejected tokens");
            //     }
            // } catch Error(string memory reason) {
            //     revert(reason);
            // } catch {
            //     revert("ERC1155: transfer to non ERC1155Receiver implementer");
            // }
        }
    }

    function _doSafeBatchTransferAcceptanceCheck(
        address operator,
        address from,
        address to,
        uint256[] memory ids,
        uint256[] memory amounts,
        bytes memory data
    )
        private
    {
        if (to.isContract()) {
            // try IERC1155Receiver(to).onERC1155BatchReceived(operator, from, ids, amounts, data) returns (bytes4 response) {
            //     if (response != IERC1155Receiver(to).onERC1155BatchReceived.selector) {
            //         revert("ERC1155: ERC1155Receiver rejected tokens");
            //     }
            // } catch Error(string memory reason) {
            //     revert(reason);
            // } catch {
            //     revert("ERC1155: transfer to non ERC1155Receiver implementer");
            // }
        }
    }

    function _asSingletonArray(uint256 element) private pure returns (uint256[] memory) {
        uint256[] memory array = new uint256[](1);
        array[0] = element;

        return array;
    }
}
