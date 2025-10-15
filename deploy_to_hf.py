#!/usr/bin/env python3
"""
🚀 Automated Hugging Face Spaces Deployment Script
Deploys the AI PDF Summarizer + QnA Bot to Hugging Face Spaces
"""

import os
import subprocess
import sys
from huggingface_hub import HfApi, Repository
from pathlib import Path

def deploy_to_hf_spaces():
    print("🚀 Starting Hugging Face Spaces Deployment...")
    
    # Configuration
    SPACE_NAME = "pdf-summarizer-qna-bot"
    USERNAME = "Abhishek210001"  # Replace with your HF username
    SPACE_ID = f"{USERNAME}/{SPACE_NAME}"
    
    try:
        # Initialize Hugging Face API
        api = HfApi()
        print(f"📡 Connecting to Hugging Face...")
        
        # Check if user is logged in
        try:
            user = api.whoami()
            print(f"✅ Logged in as: {user['name']}")
        except Exception:
            print("❌ Not logged in to Hugging Face!")
            print("Please run: huggingface-cli login")
            print("Or get your token from: https://huggingface.co/settings/tokens")
            return False
        
        # Create Space
        print(f"🏗️ Creating Space: {SPACE_ID}")
        try:
            space_url = api.create_repo(
                repo_id=SPACE_ID,
                repo_type="space",
                space_sdk="streamlit",
                private=False,
                exist_ok=True
            )
            print(f"✅ Space created/exists: {space_url}")
        except Exception as e:
            print(f"⚠️ Space creation note: {e}")
        
        # Clone the space repository
        print(f"📥 Cloning Space repository...")
        space_dir = f"./hf_space_{SPACE_NAME}"
        
        if os.path.exists(space_dir):
            print(f"🔄 Directory exists, updating...")
        else:
            Repository(
                local_dir=space_dir,
                clone_from=f"https://huggingface.co/spaces/{SPACE_ID}",
                repo_type="space"
            )
        
        # Copy files to space directory
        print("📋 Copying deployment files...")
        files_to_copy = [
            ("app.py", "app.py"),
            ("requirements.txt", "requirements.txt"), 
            ("README.md", "README.md")
        ]
        
        for src, dst in files_to_copy:
            if os.path.exists(src):
                import shutil
                dst_path = os.path.join(space_dir, dst)
                shutil.copy2(src, dst_path)
                print(f"✅ Copied {src} → {dst}")
            else:
                print(f"⚠️ File not found: {src}")
        
        # Push to Hugging Face Spaces
        print("🚀 Deploying to Hugging Face Spaces...")
        repo = Repository(local_dir=space_dir, repo_type="space")
        repo.git_add()
        repo.git_commit("🚀 Deploy AI PDF Summarizer + QnA Bot")
        repo.git_push()
        
        print("🎉 DEPLOYMENT SUCCESSFUL!")
        print(f"🌐 Your app is now live at:")
        print(f"   https://huggingface.co/spaces/{SPACE_ID}")
        print(f"   https://{USERNAME}-{SPACE_NAME}.hf.space")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

if __name__ == "__main__":
    success = deploy_to_hf_spaces()
    if success:
        print("\n✨ Deployment completed successfully!")
    else:
        print("\n💡 Please check the error messages above and try again.")
