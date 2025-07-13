
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract CarbonNFT is ERC721, ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;
    
    struct CarbonBadge {
        uint256 co2Saved;
        string badgeType;
        uint256 mintDate;
        address originalMinter;
    }
    
    mapping(uint256 => CarbonBadge) public carbonBadges;
    mapping(address => uint256[]) public userBadges;
    
    uint256 public mintingFee = 0.001 ether; // 0.001 MATIC
    
    event BadgeMinted(
        uint256 indexed tokenId,
        address indexed minter,
        uint256 co2Saved,
        string badgeType
    );
    
    constructor() ERC721("CarbonNFT", "CNFT") {}
    
    function mintCarbonBadge(
        address to,
        string memory tokenURI,
        uint256 co2Saved,
        string memory badgeType
    ) public payable returns (uint256) {
        require(msg.value >= mintingFee, "Insufficient minting fee");
        
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, tokenURI);
        
        carbonBadges[tokenId] = CarbonBadge({
            co2Saved: co2Saved,
            badgeType: badgeType,
            mintDate: block.timestamp,
            originalMinter: to
        });
        
        userBadges[to].push(tokenId);
        
        emit BadgeMinted(tokenId, to, co2Saved, badgeType);
        
        return tokenId;
    }
    
    function getUserBadges(address user) public view returns (uint256[] memory) {
        return userBadges[user];
    }
    
    function getBadgeInfo(uint256 tokenId) public view returns (CarbonBadge memory) {
        require(_exists(tokenId), "Token does not exist");
        return carbonBadges[tokenId];
    }
    
    function setMintingFee(uint256 _fee) public onlyOwner {
        mintingFee = _fee;
    }
    
    function withdraw() public onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
    
    // Override required functions
    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
    }
    
    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }
    
    function supportsInterface(bytes4 interfaceId) public view override(ERC721, ERC721URIStorage) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}
