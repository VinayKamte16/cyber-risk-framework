"""
Utility functions for the cybersecurity risk framework.
"""

import re
import ipaddress
from typing import Union, Optional

def validate_ip(ip: str) -> bool:
    """
    Validate if a string is a valid IP address (IPv4 or IPv6).
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def validate_domain(domain: str) -> bool:
    """
    Validate if a string is a valid domain name.
    """
    domain_pattern = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    )
    return bool(domain_pattern.match(domain))

def validate_hash(hash_str: str) -> Optional[str]:
    """
    Validate if a string is a valid hash and return its type.
    """
    hash_patterns = {
        'md5': re.compile(r'^[a-fA-F0-9]{32}$'),
        'sha1': re.compile(r'^[a-fA-F0-9]{40}$'),
        'sha256': re.compile(r'^[a-fA-F0-9]{64}$'),
        'sha512': re.compile(r'^[a-fA-F0-9]{128}$')
    }
    
    for hash_type, pattern in hash_patterns.items():
        if pattern.match(hash_str):
            return hash_type
    return None

def normalize_ip(ip: str) -> Optional[str]:
    """
    Normalize an IP address to its standard form.
    """
    try:
        return str(ipaddress.ip_address(ip))
    except ValueError:
        return None

def normalize_domain(domain: str) -> str:
    """
    Normalize a domain name to its lowercase form.
    """
    return domain.lower()

def calculate_entropy(data: Union[str, bytes]) -> float:
    """
    Calculate Shannon entropy of data.
    """
    if isinstance(data, str):
        data = data.encode()
    
    entropy = 0
    size = len(data)
    
    # Count byte occurrences
    byte_counts = {}
    for byte in data:
        byte_counts[byte] = byte_counts.get(byte, 0) + 1
    
    # Calculate entropy
    for count in byte_counts.values():
        probability = count / size
        entropy -= probability * log2(probability)
    
    return entropy 