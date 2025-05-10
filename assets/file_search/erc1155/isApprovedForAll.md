/**
    @notice Queries the approval status of an operator for a given owner.
    @param _owner     The owner of the tokens
    @param _operator  Address of authorized operator
    @return           True if the operator is approved, false if not
*/

$ADD POSTCONDITION HERE
function isApprovedForAll(address _owner, address _operator) public view returns (bool approved);