import re

class RootDetector:
    @staticmethod
    def got_root(hostname: str, system_info: list, target: str) -> bool:
        """
        Detect if root access has been achieved based on system information.
        """
        # Check for common root indicators in system info
        root_indicators = [
            r"root",
            r"uid=0",
            r"sudo",
            r"su",
            r"superuser",
            r"administrator",
            r"system",
            r"admin",
            target,
        ]
        
        for info in system_info:
            for indicator in root_indicators:
                if re.search(indicator, info, re.IGNORECASE):
                    return True
        
        return False