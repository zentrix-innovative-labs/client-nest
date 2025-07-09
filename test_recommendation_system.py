#!/usr/bin/env python3
"""
Comprehensive test script for the ClientNest recommendation system.
Tests both ML service and Django backend integration.
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
ML_SERVICE_URL = "http://localhost:8001"
BACKEND_URL = "http://localhost:8000"

class RecommendationSystemTester:
    def __init__(self):
        self.auth_token = None
        self.test_user_id = None
        
    def test_ml_service_health(self) -> bool:
        """Test if ML service is running and healthy."""
        print("🔍 Testing ML Service Health...")
        try:
            response = requests.get(f"{ML_SERVICE_URL}/docs")
            if response.status_code == 200:
                print("✅ ML Service is running and accessible")
                return True
            else:
                print(f"❌ ML Service health check failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ ML Service connection error: {e}")
            return False
    
    def test_ml_service_recommendations(self) -> bool:
        """Test ML service recommendation endpoint."""
        print("\n🧠 Testing ML Service Recommendations...")
        
        test_cases = [
            {
                "name": "Hybrid Algorithm",
                "data": {
                    "user_id": 1,
                    "context": {"recent_views": [1, 2, 3, 4, 5]},
                    "algorithm": "hybrid"
                }
            },
            {
                "name": "Collaborative Algorithm",
                "data": {
                    "user_id": 1,
                    "context": {"recent_views": [1, 2, 3]},
                    "algorithm": "collaborative"
                }
            },
            {
                "name": "Content-Based Algorithm",
                "data": {
                    "user_id": 1,
                    "context": {"recent_views": [1, 2, 3]},
                    "algorithm": "content"
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{ML_SERVICE_URL}/recommend",
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ {test_case['name']}: {len(result.get('recommendations', []))} recommendations")
                    print(f"   Algorithm used: {result.get('algorithm')}")
                else:
                    print(f"❌ {test_case['name']} failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ {test_case['name']} error: {e}")
                return False
        
        return True
    
    def test_ml_service_churn_prediction(self) -> bool:
        """Test ML service churn prediction endpoint."""
        print("\n📊 Testing ML Service Churn Prediction...")
        
        test_data = {
            "user_id": 1,
            "features": {
                "activity": 0.7,
                "purchases": 3,
                "last_login_days": 2,
                "total_sessions": 15
            }
        }
        
        try:
            response = requests.post(
                f"{ML_SERVICE_URL}/churn-predict",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                churn_risk = result.get('churn_risk', 0)
                print(f"✅ Churn prediction successful: {churn_risk:.2%} risk")
                return True
            else:
                print(f"❌ Churn prediction failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Churn prediction error: {e}")
            return False
    
    def create_test_user(self) -> bool:
        """Create a test user in Django backend."""
        print("\n👤 Creating Test User...")
        
        user_data = {
            "username": "testuser_recommendations",
            "email": "test.recommendations@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/auth/register/",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 201]:
                print("✅ Test user created successfully")
                return True
            else:
                print(f"❌ User creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ User creation error: {e}")
            return False
    
    def authenticate_user(self) -> bool:
        """Authenticate and get JWT token."""
        print("\n🔐 Authenticating User...")
        
        auth_data = {
            "username": "testuser_recommendations",
            "password": "testpass123"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/auth/token/",
                json=auth_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.auth_token = result.get('access')
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_backend_recommendations_api(self) -> bool:
        """Test Django backend recommendations API."""
        print("\n🎯 Testing Backend Recommendations API...")
        
        if not self.auth_token:
            print("❌ No authentication token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test different algorithms
        algorithms = ["hybrid", "collaborative", "content"]
        
        for algorithm in algorithms:
            try:
                response = requests.get(
                    f"{BACKEND_URL}/api/recommendations/recommendations/?algorithm={algorithm}&top_k=5",
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    recommendations = result.get('recommendations', [])
                    print(f"✅ {algorithm.capitalize()} recommendations: {len(recommendations)} items")
                else:
                    print(f"❌ {algorithm} recommendations failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ {algorithm} recommendations error: {e}")
                return False
        
        return True
    
    def test_backend_churn_prediction_api(self) -> bool:
        """Test Django backend churn prediction API."""
        print("\n📈 Testing Backend Churn Prediction API...")
        
        if not self.auth_token:
            print("❌ No authentication token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/recommendations/churn-prediction/",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                churn_risk = result.get('churn_risk', 0)
                risk_level = result.get('risk_level', 'unknown')
                print(f"✅ Churn prediction: {churn_risk:.2%} risk ({risk_level})")
                return True
            else:
                print(f"❌ Churn prediction failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Churn prediction error: {e}")
            return False
    
    def test_interaction_logging(self) -> bool:
        """Test interaction logging API."""
        print("\n📝 Testing Interaction Logging...")
        
        if not self.auth_token:
            print("❌ No authentication token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        test_interactions = [
            {
                "interaction_type": "view",
                "content_id": "post_123",
                "content_type": "post",
                "platform": "web",
                "metadata": {"duration": 30, "source": "homepage"}
            },
            {
                "interaction_type": "like",
                "content_id": "article_456",
                "content_type": "article",
                "platform": "mobile",
                "metadata": {"source": "feed"}
            },
            {
                "interaction_type": "click",
                "content_id": "product_789",
                "content_type": "product",
                "platform": "web",
                "metadata": {"position": 3, "category": "electronics"}
            }
        ]
        
        for i, interaction in enumerate(test_interactions, 1):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/recommendations/interactions/",
                    json=interaction,
                    headers=headers
                )
                
                if response.status_code in [200, 201]:
                    print(f"✅ Interaction {i} logged successfully")
                else:
                    print(f"❌ Interaction {i} failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Interaction {i} error: {e}")
                return False
        
        return True
    
    def test_recommendation_stats(self) -> bool:
        """Test recommendation statistics API."""
        print("\n📊 Testing Recommendation Statistics...")
        
        if not self.auth_token:
            print("❌ No authentication token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/recommendations/stats/",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                total_recs = result.get('total_recommendations', 0)
                ctr = result.get('click_through_rate', 0)
                print(f"✅ Stats retrieved: {total_recs} total recommendations, {ctr:.1%} CTR")
                return True
            else:
                print(f"❌ Stats failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Stats error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests and provide a summary."""
        print("🚀 Starting Comprehensive Recommendation System Test")
        print("=" * 60)
        
        test_results = []
        
        # ML Service Tests
        test_results.append(("ML Service Health", self.test_ml_service_health()))
        test_results.append(("ML Service Recommendations", self.test_ml_service_recommendations()))
        test_results.append(("ML Service Churn Prediction", self.test_ml_service_churn_prediction()))
        
        # Backend Integration Tests
        test_results.append(("User Creation", self.create_test_user()))
        test_results.append(("User Authentication", self.authenticate_user()))
        test_results.append(("Backend Recommendations API", self.test_backend_recommendations_api()))
        test_results.append(("Backend Churn Prediction API", self.test_backend_churn_prediction_api()))
        test_results.append(("Interaction Logging", self.test_interaction_logging()))
        test_results.append(("Recommendation Statistics", self.test_recommendation_stats()))
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
            if result:
                passed += 1
        
        print(f"\n🎯 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Your recommendation system is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
        return passed == total

if __name__ == "__main__":
    tester = RecommendationSystemTester()
    success = tester.run_all_tests()
    exit(0 if success else 1) 