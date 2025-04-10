import re

class RootDetector:
    @staticmethod
    def got_root(hostname: str, output: str) -> bool:
        patterns = [
            re.compile("^# $"),
            re.compile("^bash-[0-9]+.[0-9]# $"),
            re.compile(f"root@{hostname}:.*#\s"),
            re.compile("uid=0\(root\)"),
            re.compile("^root$")
        ]
        
        if any(pattern.search(output) for pattern in patterns):
            return True
        if f"root@{hostname}:" in output:
            return True
        return False