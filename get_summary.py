#!/usr/bin/env python3
"""
Get summary from AI Document Analyzer
Usage: python get_summary.py DOCUMENT_ID
"""
import sys
import json
import requests

def get_summary(doc_id):
    response = requests.get(f"http://localhost:8000/documents/{doc_id}")
    data = response.json()
    
    print("=" * 60)
    print(f"DOCUMENT: {data['document']['filename']}")
    print(f"STATUS: {data['document']['status']}")
    print("=" * 60)
    
    if data.get("summary"):
        print("\nEXECUTIVE SUMMARY:")
        print("-" * 60)
        print(data["summary"]["executive_summary"])
        print("\nKEY POINTS:")
        print("-" * 60)
        for i, point in enumerate(data["summary"]["key_points"], 1):
            print(f"{i}. {point}")
    else:
        print("\nNo summary available yet.")
    
    if data.get("risks"):
        print("\nRISKS:")
        print("-" * 60)
        for risk in data["risks"]:
            print(f"  • {risk['title']} ({risk['severity']})")
            print(f"    {risk['description'][:80]}...")
            print(f"    Recommendation: {risk['recommendation']}")
            print()

if __name__ == "__main__":
    doc_id = sys.argv[1] if len(sys.argv) > 1 else "2a8e14ed-3c74-49ec-a074-27411dd8eed3"
    get_summary(doc_id)