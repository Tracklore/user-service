#!/usr/bin/env python3
"""
Script to generate secure secrets for the application.
"""

import secrets
import argparse

def generate_secret_key(length=32):
    """Generate a secure random secret key."""
    return secrets.token_hex(length)

def main():
    parser = argparse.ArgumentParser(description="Generate secure secrets for the application")
    parser.add_argument("--length", type=int, default=32, help="Length of the secret key (default: 32)")
    
    args = parser.parse_args()
    
    print("Generated secure secret key:")
    print(generate_secret_key(args.length))

if __name__ == "__main__":
    main()