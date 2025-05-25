import os
import requests
import pytest

# Assuming the Flask app runs on localhost:5000
BASE_URL = "http://localhost:5000/api" 

# Environment variable for the GitHub Personal Access Token
GITHUB_PAT_ENV_VAR = "GITHUB_PAT"

@pytest.fixture(scope="module")
def jwt_token():
    pat = os.environ.get(GITHUB_PAT_ENV_VAR)
    if not pat:
        pytest.fail(f"Environment variable {GITHUB_PAT_ENV_VAR} not set.")

    login_url = f"{BASE_URL}/login"
    response = requests.post(login_url, json={"personalAccessToken": pat})
    
    if response.status_code != 200:
        pytest.fail(f"Login failed: {response.status_code} - {response.text}")
    
    return response.json()["accessToken"]

def test_me_endpoint(jwt_token):
    me_url = f"{BASE_URL}/me"
    headers = {"Authorization": f"Bearer {jwt_token}"}
    
    response = requests.get(me_url, headers=headers)
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    
    data = response.json()
    assert "avatarUrl" in data, "Response JSON should contain 'avatarUrl'"
    assert "name" in data, "Response JSON should contain 'name'"
