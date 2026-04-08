// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title IdentityRegistry
 * @dev ERC-721 based agent identity contract for APEX
 * @author DR. PRIYA NAIR - VP of Trust & Compliance at APEX
 * @notice Manages agent identity NFTs with IPFS metadata storage
 */
contract IdentityRegistry is ERC721URIStorage, Ownable {
    
    // State variables
    uint256 private _nextTokenId;
    mapping(address => bool) private _registeredAgents;
    mapping(uint256 => address) private _tokenOwners;
    
    // Events
    event AgentRegistered(
        uint256 indexed tokenId,
        address indexed agent,
        string cardURI
    );
    
    /**
     * @dev Constructor
     */
    constructor() ERC721("APEX Agent Identity", "APEX-AI") {
        _nextTokenId = 1;
        _transferOwnership(msg.sender);
    }
    
    /**
     * @notice Mint a new agent identity NFT
     * @dev Only contract owner can mint new agent identities
     * @param to Address to mint the NFT to
     * @param agentCardURI IPFS URI of the agent card metadata
     * @return tokenId The ID of the newly minted token
     */
    function mintAgentNFT(address to, string memory agentCardURI) 
        external 
        onlyOwner 
        returns (uint256 tokenId) 
    {
        require(to != address(0), "IdentityRegistry: Cannot mint to zero address");
        require(bytes(agentCardURI).length > 0, "IdentityRegistry: Agent card URI required");
        
        tokenId = _nextTokenId;
        _nextTokenId++;
        
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, agentCardURI);
        
        _registeredAgents[to] = true;
        _tokenOwners[tokenId] = to;
        
        emit AgentRegistered(tokenId, to, agentCardURI);
    }
    
    /**
     * @notice Get the agent card URI for a token
     * @param tokenId The token ID to query
     * @return The IPFS URI of the agent card
     */
    function getAgentCard(uint256 tokenId) 
        external 
        view 
        returns (string memory) 
    {
        require(ownerOf(tokenId) != address(0), "IdentityRegistry: Token does not exist");
        return tokenURI(tokenId);
    }
    
    /**
     * @notice Check if an address is a registered agent
     * @param agent The address to check
     * @return True if the address is a registered agent
     */
    function isRegistered(address agent) 
        external 
        view 
        returns (bool) 
    {
        return _registeredAgents[agent];
    }
    
    /**
     * @notice Get the owner of a token
     * @param tokenId The token ID to query
     * @return The address of the token owner
     */
    function getAgentOwner(uint256 tokenId) 
        external 
        view 
        returns (address) 
    {
        require(ownerOf(tokenId) != address(0), "IdentityRegistry: Token does not exist");
        return ownerOf(tokenId);
    }
    
    /**
     * @notice Get the next token ID that will be minted
     * @return The next token ID
     */
    function getNextTokenId() 
        external 
        view 
        returns (uint256) 
    {
        return _nextTokenId;
    }
    
    /**
     * @notice Get total number of registered agents
     * @return Total supply of agent NFTs
     */
    function totalRegisteredAgents() 
        external 
        view 
        returns (uint256) 
    {
        return _nextTokenId;
    }
    
    // Override required functions
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId,
        uint256 batchSize
    ) internal override {
        super._beforeTokenTransfer(from, to, tokenId, batchSize);
        
        if (from != address(0)) {
            _registeredAgents[from] = false;
        }
        
        if (to != address(0)) {
            _registeredAgents[to] = true;
            _tokenOwners[tokenId] = to;
        }
    }
}
