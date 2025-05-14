```solidity

pragma solidity ^0.5.0;

contract ERC123Identity {

    
    address public owner;
    address public trustedVerifier;

    constructor() public {
        owner = msg.sender;
    }

    struct Identity {
        address owner;
        address dataHash;
        bool verified;
    }

    mapping(bytes32 => Identity) private identities;
    mapping(address => mapping(bytes32 => bool)) private consents;

    event IdentityCreated(address indexed owner, bytes32 identityId);
    event IdentityUpdated(address indexed owner, bytes32 identityId);
    event IdentityVerified(address indexed owner, bytes32 identityId, bool verified);
    event ConsentGiven(address indexed owner, address indexed caller, bytes32 identityId);
    event ConsentRevoked(address indexed owner, address indexed caller, bytes32 identityId);

    $ADD POSTCONDITION HERE
    function createIdentity(bytes32 identityId) external;

    $ADD POSTCONDITION HERE
    function updateIdentity(bytes32 identityId, address newDataHash) external;

    $ADD POSTCONDITION HERE
    function verifyIdentity(bytes32 identityId) external view returns (bool ret);
    
    $ADD POSTCONDITION HERE
    function giveConsent(address caller, bytes32 identityId) external;

    $ADD POSTCONDITION HERE
    function revokeConsent(address caller, bytes32 identityId) external;

    $ADD POSTCONDITION HERE
    function hasConsent(address caller, bytes32 identityId) external view returns (bool ret);

    $ADD POSTCONDITION HERE
    function verifyIdentityByTrustedVerifier(bytes32 identityId, bool verified) external;
}
```