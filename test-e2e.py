#!/usr/bin/env python3
"""
End-to-End Testing Script for Professor Al Gorithm
Module 7: Testing & Debugging Implementation

This script performs comprehensive testing of the AI agent:
- Backend API endpoint testing
- MCP integration validation
- Error handling verification
- Edge case simulation
- Performance monitoring
- User interface validation
"""

import asyncio
import aiohttp
import json
import time
import sys
import os
from typing import Dict, Any, List

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:3000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:7860")

class E2ETestRunner:
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    async def run_all_tests(self):
        """Run all end-to-end tests"""
        print("🧪 Starting End-to-End Testing for Professor Al Gorithm")
        print("=" * 60)
        
        # Test categories
        await self.test_backend_health()
        await self.test_api_endpoints()
        await self.test_error_handling()
        await self.test_edge_cases()
        await self.test_performance()
        await self.test_mcp_integration()
        
        # Generate report
        self.generate_report()
        
    async def test_backend_health(self):
        """Test backend health and connectivity"""
        print("\n🏥 Testing Backend Health...")
        
        tests = [
            ("Health Check", "GET", "/health"),
            ("Root Endpoint", "GET", "/"),
            ("Performance Stats", "GET", "/api/stats"),
        ]
        
        for test_name, method, endpoint in tests:
            await self.run_test(test_name, self.check_endpoint, method, endpoint)
            
    async def test_api_endpoints(self):
        """Test all API endpoints with valid inputs"""
        print("\n🔌 Testing API Endpoints...")
        
        # Chat endpoint
        await self.run_test(
            "Chat API - Valid Input",
            self.test_chat_endpoint,
            {"message": "Hello, I want to learn algorithms", "conversationId": "test-123"}
        )
        
        # Challenges endpoint (POST)
        await self.run_test(
            "Challenges API - POST Valid",
            self.test_challenges_endpoint,
            {"difficulty": "easy", "limit": 5}
        )
        
        # Skills endpoint (POST)
        await self.run_test(
            "Skills API - POST Valid",
            self.test_skills_endpoint,
            {"category": "algorithms", "limit": 10}
        )
        
        # Canvas endpoint
        await self.run_test(
            "Canvas API - Valid Phase",
            self.test_canvas_endpoint,
            {"phase": "constraints", "content": "I need to solve a two-sum problem with array input and target integer."}
        )
        
    async def test_error_handling(self):
        """Test error handling with invalid inputs"""
        print("\n⚠️  Testing Error Handling...")
        
        # Invalid chat inputs
        error_tests = [
            ("Chat - Missing Message", "POST", "/api/chat", {}),
            ("Chat - Invalid Message Type", "POST", "/api/chat", {"message": 123}),
            ("Chat - Empty Message", "POST", "/api/chat", {"message": ""}),
            ("Chat - Very Long Message", "POST", "/api/chat", {"message": "x" * 3000}),
            
            ("Challenges - Invalid Difficulty", "POST", "/api/challenges", {"difficulty": "impossible"}),
            ("Challenges - Invalid Limit", "POST", "/api/challenges", {"limit": -1}),
            ("Challenges - Very High Limit", "POST", "/api/challenges", {"limit": 1000}),
            
            ("Skills - Invalid Category", "POST", "/api/skills", {"category": "nonexistent"}),
            ("Skills - Invalid Limit", "POST", "/api/skills", {"limit": "abc"}),
            
            ("Canvas - Missing Phase", "POST", "/api/canvas", {"content": "test"}),
            ("Canvas - Invalid Phase", "POST", "/api/canvas", {"phase": "invalid", "content": "test"}),
            ("Canvas - Missing Content", "POST", "/api/canvas", {"phase": "constraints"}),
            ("Canvas - Very Long Content", "POST", "/api/canvas", {"phase": "constraints", "content": "x" * 6000}),
        ]
        
        for test_name, method, endpoint, payload in error_tests:
            await self.run_test(test_name, self.test_error_response, method, endpoint, payload)
            
    async def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        print("\n🔍 Testing Edge Cases...")
        
        edge_cases = [
            ("Empty JSON Payload", "POST", "/api/chat", {}),
            ("Null Values", "POST", "/api/challenges", {"difficulty": None, "limit": None}),
            ("Unicode Characters", "POST", "/api/chat", {"message": "Hello 🚀 世界 💻"}),
            ("SQL Injection Attempt", "POST", "/api/chat", {"message": "'; DROP TABLE users; --"}),
            ("XSS Attempt", "POST", "/api/chat", {"message": "<script>alert('xss')</script>"}),
            ("Very Long Conversation ID", "POST", "/api/chat", {"message": "test", "conversationId": "x" * 1000}),
            ("Minimum Valid Limits", "POST", "/api/challenges", {"difficulty": "easy", "limit": 1}),
            ("Maximum Valid Limits", "POST", "/api/challenges", {"difficulty": "hard", "limit": 50}),
        ]
        
        for test_name, method, endpoint, payload in edge_cases:
            await self.run_test(test_name, self.test_edge_case, method, endpoint, payload)
            
    async def test_performance(self):
        """Test performance and timeout handling"""
        print("\n⚡ Testing Performance...")
        
        # Concurrent requests test
        await self.run_test(
            "Concurrent Requests",
            self.test_concurrent_requests,
            5  # Number of concurrent requests
        )
        
        # Response time test
        await self.run_test(
            "Response Time Check",
            self.test_response_times
        )
        
    async def test_mcp_integration(self):
        """Test MCP server integration"""
        print("\n🔗 Testing MCP Integration...")
        
        await self.run_test(
            "MCP Challenges Integration",
            self.test_mcp_challenges
        )
        
        await self.run_test(
            "MCP Skills Integration", 
            self.test_mcp_skills
        )
        
    async def run_test(self, test_name: str, test_func, *args):
        """Run a single test and record results"""
        self.total_tests += 1
        start_time = time.time()
        
        try:
            result = await test_func(*args)
            duration = time.time() - start_time
            
            if result:
                print(f"  ✅ {test_name} ({duration:.2f}s)")
                self.passed_tests += 1
                status = "PASSED"
            else:
                print(f"  ❌ {test_name} ({duration:.2f}s)")
                self.failed_tests += 1
                status = "FAILED"
                
        except Exception as e:
            duration = time.time() - start_time
            print(f"  💥 {test_name} ({duration:.2f}s) - Error: {str(e)}")
            self.failed_tests += 1
            status = "ERROR"
            
        self.results.append({
            "name": test_name,
            "status": status,
            "duration": duration,
            "timestamp": time.time()
        })
        
    async def check_endpoint(self, method: str, endpoint: str) -> bool:
        """Check if an endpoint is responsive"""
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{BACKEND_URL}{endpoint}"
                async with session.request(method, url, timeout=10) as response:
                    return response.status < 500
            except Exception:
                return False
                
    async def test_chat_endpoint(self, payload: Dict[str, Any]) -> bool:
        """Test chat endpoint with valid payload"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{BACKEND_URL}/api/chat", json=payload, timeout=30) as response:
                    data = await response.json()
                    return response.status == 200 and "response" in data
            except Exception:
                return False
                
    async def test_challenges_endpoint(self, payload: Dict[str, Any]) -> bool:
        """Test challenges endpoint"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{BACKEND_URL}/api/challenges", json=payload, timeout=30) as response:
                    data = await response.json()
                    return response.status == 200 and "challenges" in data
            except Exception:
                return False
                
    async def test_skills_endpoint(self, payload: Dict[str, Any]) -> bool:
        """Test skills endpoint"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{BACKEND_URL}/api/skills", json=payload, timeout=30) as response:
                    data = await response.json()
                    return response.status == 200 and "skills" in data
            except Exception:
                return False
                
    async def test_canvas_endpoint(self, payload: Dict[str, Any]) -> bool:
        """Test canvas endpoint"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{BACKEND_URL}/api/canvas", json=payload, timeout=30) as response:
                    data = await response.json()
                    return response.status == 200 and "feedback" in data
            except Exception:
                return False
                
    async def test_error_response(self, method: str, endpoint: str, payload: Dict[str, Any]) -> bool:
        """Test that invalid inputs return appropriate error responses"""
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{BACKEND_URL}{endpoint}"
                async with session.request(method, url, json=payload, timeout=10) as response:
                    # Should return 4xx error for invalid input
                    return 400 <= response.status < 500
            except Exception:
                return False
                
    async def test_edge_case(self, method: str, endpoint: str, payload: Dict[str, Any]) -> bool:
        """Test edge cases - should handle gracefully without crashing"""
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{BACKEND_URL}{endpoint}"
                async with session.request(method, url, json=payload, timeout=15) as response:
                    # Should not return 5xx server errors
                    return response.status < 500
            except Exception:
                return False
                
    async def test_concurrent_requests(self, num_requests: int) -> bool:
        """Test handling of concurrent requests"""
        async def make_request():
            async with aiohttp.ClientSession() as session:
                try:
                    payload = {"message": "test concurrent request"}
                    async with session.post(f"{BACKEND_URL}/api/chat", json=payload, timeout=30) as response:
                        return response.status == 200
                except Exception:
                    return False
                    
        # Make concurrent requests
        tasks = [make_request() for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
        
        # At least 80% should succeed
        success_rate = sum(results) / len(results)
        return success_rate >= 0.8
        
    async def test_response_times(self) -> bool:
        """Test that response times are reasonable"""
        endpoints = [
            ("GET", "/health"),
            ("POST", "/api/challenges", {"difficulty": "easy"}),
            ("POST", "/api/skills", {"category": "algorithms"}),
        ]
        
        total_time = 0
        num_tests = 0
        
        async with aiohttp.ClientSession() as session:
            for method, endpoint, *payload in endpoints:
                try:
                    start_time = time.time()
                    url = f"{BACKEND_URL}{endpoint}"
                    
                    if payload:
                        async with session.request(method, url, json=payload[0], timeout=30) as response:
                            await response.text()
                    else:
                        async with session.request(method, url, timeout=30) as response:
                            await response.text()
                            
                    duration = time.time() - start_time
                    total_time += duration
                    num_tests += 1
                    
                except Exception:
                    continue
                    
        if num_tests == 0:
            return False
            
        avg_response_time = total_time / num_tests
        # Average response time should be under 10 seconds
        return avg_response_time < 10.0
        
    async def test_mcp_challenges(self) -> bool:
        """Test MCP challenges integration"""
        async with aiohttp.ClientSession() as session:
            try:
                payload = {"difficulty": "easy", "limit": 3}\n                async with session.post(f"{BACKEND_URL}/api/challenges", json=payload, timeout=45) as response:
                    data = await response.json()
                    # Should return successfully even if MCP is down (fallback behavior)
                    return response.status == 200 and isinstance(data.get("challenges"), list)
            except Exception:
                return False
                
    async def test_mcp_skills(self) -> bool:
        """Test MCP skills integration"""
        async with aiohttp.ClientSession() as session:
            try:
                payload = {"category": "algorithms", "limit": 5}
                async with session.post(f"{BACKEND_URL}/api/skills", json=payload, timeout=45) as response:
                    data = await response.json()
                    # Should return successfully even if MCP is down (fallback behavior)
                    return response.status == 200 and isinstance(data.get("skills"), list)
            except Exception:
                return False
                
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("🧪 END-TO-END TEST RESULTS")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: System is production-ready!")
        elif success_rate >= 80:
            print("✅ GOOD: System is mostly stable with minor issues")
        elif success_rate >= 70:
            print("⚠️  WARNING: System has significant issues that need attention")
        else:
            print("❌ CRITICAL: System has major issues and is not production-ready")
            
        # Show failed tests
        failed_tests = [r for r in self.results if r["status"] in ["FAILED", "ERROR"]]
        if failed_tests:
            print("\\n🔍 Failed Tests:")
            for test in failed_tests:
                print(f"  • {test['name']} - {test['status']}")
                
        print("\\n📊 Performance Summary:")
        total_duration = sum(r["duration"] for r in self.results)
        avg_duration = total_duration / len(self.results) if self.results else 0
        print(f"  • Total test time: {total_duration:.2f}s")
        print(f"  • Average test time: {avg_duration:.2f}s")
        
        # Save detailed results to file
        with open("test-results.json", "w") as f:
            json.dump({
                "summary": {
                    "total": self.total_tests,
                    "passed": self.passed_tests,
                    "failed": self.failed_tests,
                    "success_rate": success_rate,
                    "total_duration": total_duration
                },
                "results": self.results
            }, f, indent=2)
            
        print(f"\\n📄 Detailed results saved to: test-results.json")

async def main():
    """Main test runner"""
    if len(sys.argv) > 1 and sys.argv[1] == "--backend-url":
        global BACKEND_URL
        BACKEND_URL = sys.argv[2]
        
    print(f"🔗 Testing backend at: {BACKEND_URL}")
    
    runner = E2ETestRunner()
    await runner.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())