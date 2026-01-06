"""
Test script to verify JWT authentication system.
Run this after starting the backend server.
"""
import asyncio
import httpx


BASE_URL = "http://localhost:8000"


async def test_auth_flow():
    """Test the complete authentication flow."""
    print("🧪 Testing JWT Authentication Flow\n")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Signup
        print("\n1️⃣  Testing Signup...")
        signup_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/auth/signup", json=signup_data)
            if response.status_code == 201:
                data = response.json()
                print(f"✅ Signup successful!")
                print(f"   User ID: {data['user']['id']}")
                print(f"   Email: {data['user']['email']}")
                print(f"   Access Token: {data['access_token'][:50]}...")
                access_token = data['access_token']
                refresh_token = data['refresh_token']
            elif response.status_code == 400:
                print(f"⚠️  User already exists, trying login instead...")
                # User exists, try login
                login_response = await client.post(
                    f"{BASE_URL}/auth/login",
                    json={"email": signup_data["email"], "password": signup_data["password"]}
                )
                if login_response.status_code == 200:
                    data = login_response.json()
                    print(f"✅ Login successful!")
                    access_token = data['access_token']
                    refresh_token = data['refresh_token']
                else:
                    print(f"❌ Login failed: {login_response.text}")
                    return
            else:
                print(f"❌ Signup failed: {response.text}")
                return
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        # Test 2: Get Current User
        print("\n2️⃣  Testing Get Current User (Protected Route)...")
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(f"{BASE_URL}/auth/me", headers=headers)
            if response.status_code == 200:
                user = response.json()
                print(f"✅ Successfully retrieved user info")
                print(f"   Name: {user['full_name']}")
                print(f"   Email: {user['email']}")
                print(f"   Active: {user['is_active']}")
            else:
                print(f"❌ Failed: {response.text}")
                return
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        # Test 3: Token Refresh
        print("\n3️⃣  Testing Token Refresh...")
        try:
            response = await client.post(
                f"{BASE_URL}/auth/refresh",
                json={"refresh_token": refresh_token}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Token refresh successful!")
                print(f"   New Access Token: {data['access_token'][:50]}...")
                access_token = data['access_token']
            else:
                print(f"❌ Failed: {response.text}")
                return
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        # Test 4: Logout
        print("\n4️⃣  Testing Logout...")
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.post(f"{BASE_URL}/auth/logout", headers=headers)
            if response.status_code == 200:
                print(f"✅ Logout successful!")
                print(f"   Message: {response.json()['message']}")
            else:
                print(f"❌ Failed: {response.text}")
                return
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        # Test 5: Verify token is invalidated
        print("\n5️⃣  Testing Token Invalidation (should fail)...")
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(f"{BASE_URL}/auth/me", headers=headers)
            if response.status_code == 401:
                print(f"✅ Token correctly invalidated after logout")
            else:
                print(f"⚠️  Warning: Token still valid after logout")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!\n")


if __name__ == "__main__":
    print("Starting authentication tests...")
    print("Make sure the backend server is running on http://localhost:8000\n")
    
    try:
        asyncio.run(test_auth_flow())
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
