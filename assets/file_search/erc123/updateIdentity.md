**updateIdentity(bytes32 identityId, address newDataHash)**
- **Description**: Updates the hash of the data associated with an existing identity. This can be done by the owner or any caller who has been given consent. If the identity is verified and the hash is different, it should be reset.
- **Parameters**:
    - `identityId`: The unique identifier for the identity to be updated.
    - `newDataHash`: The hash of the new data to be associated with the identity.
- **Events**:
    - `IdentityUpdated`: Emitted when an identity is successfully updated.

$ADD POSTCONDITION HERE
function updateIdentity(bytes32 identityId, address newDataHash) external;