#!/usr/bin/env python3
"""
Security Verification Script for ClientNest Microservices
Checks that DEBUG settings are properly configured across all services
"""

import os
import re
import sys
from pathlib import Path

def check_debug_configuration():
    """Check DEBUG configuration in all microservices"""
    
    base_dir = Path(__file__).parent
    microservices_dir = base_dir / "microservices"
    
    if not microservices_dir.exists():
        print("❌ Microservices directory not found!")
        return False
    
    print("🔍 Checking DEBUG configuration in all microservices...\n")
    
    issues_found = []
    services_checked = 0
    
    # Define patterns to look for
    dangerous_patterns = [
        r'DEBUG\s*=\s*True',
        r'DEBUG\s*=\s*config\([^)]*default\s*=\s*True',
        r'DEBUG\s*=\s*os\.environ\.get\([^)]*\)\s*!=\s*[\'"]False[\'"]',
    ]
    
    safe_patterns = [
        r'DEBUG\s*=\s*config\([^)]*default\s*=\s*False',
        r'DEBUG\s*=\s*os\.environ\.get\([^)]*[\'"]False[\'"]',
    ]
    
    for service_dir in microservices_dir.iterdir():
        if service_dir.is_dir():
            # Look for settings files
            settings_files = list(service_dir.glob("**/settings*.py"))
            
            for settings_file in settings_files:
                services_checked += 1
                print(f"📄 Checking: {settings_file.relative_to(base_dir)}")
                
                try:
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for dangerous patterns
                    for pattern in dangerous_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            issues_found.append({
                                'file': settings_file.relative_to(base_dir),
                                'issue': f"Dangerous DEBUG pattern found: {matches[0]}",
                                'severity': 'HIGH'
                            })
                    
                    # Check for safe patterns
                    has_safe_pattern = False
                    for pattern in safe_patterns:
                        if re.search(pattern, content):
                            has_safe_pattern = True
                            break
                    
                    if not has_safe_pattern and 'DEBUG' in content:
                        issues_found.append({
                            'file': settings_file.relative_to(base_dir),
                            'issue': "DEBUG setting found but pattern not recognized as secure",
                            'severity': 'MEDIUM'
                        })
                    
                    # Check for hardcoded sensitive values
                    if re.search(r'SECRET_KEY\s*=\s*[\'"][^\'\"]*insecure[^\'\"]*[\'"]', content):
                        issues_found.append({
                            'file': settings_file.relative_to(base_dir),
                            'issue': "Hardcoded insecure SECRET_KEY found",
                            'severity': 'MEDIUM'
                        })
                    
                    print(f"   ✅ Checked {settings_file.name}")
                    
                except Exception as e:
                    print(f"   ❌ Error reading {settings_file}: {e}")
                    issues_found.append({
                        'file': settings_file.relative_to(base_dir),
                        'issue': f"Could not read file: {e}",
                        'severity': 'LOW'
                    })
    
    print(f"\n📊 Summary:")
    print(f"   Services checked: {services_checked}")
    print(f"   Issues found: {len(issues_found)}")
    
    if issues_found:
        print(f"\n⚠️  Security Issues Found:")
        for issue in issues_found:
            severity_icon = "🔴" if issue['severity'] == 'HIGH' else "🟡" if issue['severity'] == 'MEDIUM' else "🔵"
            print(f"   {severity_icon} {issue['severity']}: {issue['file']}")
            print(f"      └─ {issue['issue']}")
        
        return False
    else:
        print(f"\n✅ All settings files have secure DEBUG configuration!")
        return True

def check_env_example():
    """Check if .env.example exists and has proper structure"""
    
    base_dir = Path(__file__).parent
    env_example = base_dir / ".env.example"
    
    print(f"\n🔍 Checking .env.example file...")
    
    if not env_example.exists():
        print(f"❌ .env.example not found at {env_example}")
        return False
    
    try:
        with open(env_example, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_vars = [
            'DEBUG',
            'SECRET_KEY',
            'ALLOWED_HOSTS',
            'DATABASE_URL'
        ]
        
        missing_vars = []
        for var in required_vars:
            if f"{var}=" not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables in .env.example: {', '.join(missing_vars)}")
            return False
        
        # Check DEBUG default
        if "DEBUG=true" in content:
            print(f"✅ .env.example has DEBUG=true (appropriate for development template)")
        else:
            print(f"⚠️  .env.example should have DEBUG=true as default for development")
        
        print(f"✅ .env.example looks good!")
        return True
        
    except Exception as e:
        print(f"❌ Error reading .env.example: {e}")
        return False

def main():
    """Main function to run all security checks"""
    
    print("🛡️  ClientNest Security Configuration Checker")
    print("=" * 50)
    
    debug_ok = check_debug_configuration()
    env_ok = check_env_example()
    
    print("\n" + "=" * 50)
    
    if debug_ok and env_ok:
        print("🎉 All security checks passed!")
        sys.exit(0)
    else:
        print("❌ Security issues found. Please review and fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
