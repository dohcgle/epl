import urllib.request
import urllib.parse
import json
import os
import mimetypes

def verify():
    url = 'http://localhost/api/process/'
    file_path = 'material/TURAYEV ISROIL BURIYEVICH.xlsx'
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    print(f"Uploading {file_path}...")
    
    # Simple multipart upload using urllib is painful.
    # I will just use curl via subprocess if requests is missing, or rely on curl command in terminal.
    # But for python script:
    try:
        import requests
        print("Using requests library.")
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
            print(f"Status: {response.status_code}")
            print(f"Body: {response.text}")
    except ImportError:
        print("Requests library not found. Please install it or use curl:")
        print(f'curl -X POST -F "file=@{file_path}" {url}')

if __name__ == "__main__":
    verify()
