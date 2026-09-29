"""
Safe Automation Action Registry & Allowlist for Phase 6.

This module contains ONLY predefined, simulated Python automation functions.
NO operating system commands, subprocesses, subshells, exec, or eval are used.
"""

def restart_nginx():
    return {
        "success": True,
        "message": "Nginx restart simulated successfully."
    }

def restart_apache():
    return {
        "success": True,
        "message": "Apache restart simulated successfully."
    }

def check_disk_space():
    return {
        "success": True,
        "message": "Disk space check simulated successfully."
    }

def check_network():
    return {
        "success": True,
        "message": "Network diagnostic simulated successfully."
    }

def restart_postgresql():
    return {
        "success": True,
        "message": "PostgreSQL service restart simulated successfully."
    }

def restart_mysql():
    return {
        "success": True,
        "message": "MySQL service restart simulated successfully."
    }

def check_dns():
    return {
        "success": True,
        "message": "DNS resolution diagnostic simulated successfully."
    }

def restart_application():
    return {
        "success": True,
        "message": "Application service restart simulated successfully."
    }

def clear_application_cache():
    return {
        "success": True,
        "message": "Application cache clearing simulated successfully."
    }

def check_ssl_certificate():
    return {
        "success": True,
        "message": "SSL certificate verification simulated successfully."
    }

def check_cpu_usage():
    return {
        "success": True,
        "message": "CPU usage diagnostic simulated successfully."
    }

def check_memory_usage():
    return {
        "success": True,
        "message": "Memory usage diagnostic simulated successfully."
    }

def simulate_failure():
    return {
        "success": False,
        "message": "Simulation failed: Simulated action failure."
    }

def simulate_verification_failure():
    return {
        "success": True,
        "message": "Simulated action executed successfully."
    }

# Backward compatibility aliases
safe_restart_nginx = restart_nginx
safe_restart_apache = restart_apache
safe_check_disk_space = check_disk_space
safe_check_network = check_network
safe_restart_postgresql = restart_postgresql
safe_simulate_failure = simulate_failure

# Predefined Safe Action Allowlist
SAFE_ACTIONS = {
    "restart_nginx": restart_nginx,
    "restart_apache": restart_apache,
    "check_disk_space": check_disk_space,
    "check_network": check_network,
    "restart_postgresql": restart_postgresql,
    "restart_mysql": restart_mysql,
    "check_dns": check_dns,
    "restart_application": restart_application,
    "clear_application_cache": clear_application_cache,
    "check_ssl_certificate": check_ssl_certificate,
    "check_cpu_usage": check_cpu_usage,
    "check_memory_usage": check_memory_usage,
    "simulate_failure": simulate_failure,
    "simulate_verification_failure": simulate_verification_failure,
}

# Part 7 & 8: Reversible Action & Dry-Run Safety Metadata Registry
ACTION_METADATA = {
    "restart_nginx": {
        "action_name": "restart_nginx",
        "description": "Simulates restarting the Nginx web server service.",
        "mode": "Simulation",
        "expected_result": "Nginx restart would be simulated.",
        "risk": "Low",
        "command": "None",
        "reversible": True,
        "rollback_description": "Restore previous simulated service state."
    },
    "restart_apache": {
        "action_name": "restart_apache",
        "description": "Simulates restarting the Apache HTTP server daemon.",
        "mode": "Simulation",
        "expected_result": "Apache restart would be simulated.",
        "risk": "Low",
        "command": "None",
        "reversible": True,
        "rollback_description": "Restore previous simulated service state."
    },
    "check_disk_space": {
        "action_name": "check_disk_space",
        "description": "Simulates inspecting storage partition utilisation and temporary file growth.",
        "mode": "Simulation",
        "expected_result": "Disk space check would be simulated.",
        "risk": "Low",
        "command": "None",
        "reversible": True,
        "rollback_description": "Read-only inspection; no rollback required."
    },
    "check_network": {
        "action_name": "check_network",
        "description": "Simulates testing gateway connectivity and latency ping health.",
        "mode": "Simulation",
        "expected_result": "Network diagnostic would be simulated.",
        "risk": "Low",
        "command": "None",
        "reversible": True,
        "rollback_description": "Diagnostic query; no rollback required."
    },
    "restart_postgresql": {
        "action_name": "restart_postgresql",
        "description": "Simulates restarting the PostgreSQL database service process.",
        "mode": "Simulation",
        "expected_result": "PostgreSQL service restart would be simulated.",
        "risk": "Medium",
        "command": "None",
        "reversible": True,
        "rollback_description": "Restore previous simulated service state."
    },
    "restart_mysql": {
        "action_name": "restart_mysql",
        "description": "Simulates restarting the MySQL relational database daemon.",
        "mode": "Simulation",
        "expected_result": "MySQL restart would be simulated.",
        "risk": "Medium",
        "command": "None",
        "reversible": True,
        "rollback_description": "Restore previous simulated service state."
    },
    "check_dns": {
        "action_name": "check_dns",
        "description": "Simulates performing DNS resolution queries against configured nameservers.",
        "mode": "Simulation",
        "expected_result": "DNS resolution diagnostic would be simulated.",
        "risk": "Low",
        "command": "None",
        "reversible": True,
        "rollback_description": "Diagnostic query; no rollback required."
    },
    "restart_application": {
        "action_name": "restart_application",
        "description": "Simulates cycling the application process worker pool.",
        "mode": "Simulation",
        "expected_result": "Application service restart would be simulated.",
        "risk": "Medium",
        "command": "None",
        "reversible": True,
        "rollback_description": "Restore previous simulated service state."
    },
    "clear_application_cache": {
        "action_name": "clear_application_cache",
        "description": "Simulates flushing stale application cache entries.",
        "mode": "Simulation",
        "expected_result": "Application cache flush would be simulated.",
        "risk": "Low",
        "command": "None",
        "reversible": True,
        "rollback_description": "Re-populate cache entries on subsequent requests."
    },
    "check_ssl_certificate": {
        "action_name": "check_ssl_certificate",
        "description": "Simulates testing TLS certificate validity and expiry dates.",
        "mode": "Simulation",
        "expected_result": "SSL certificate verification would be simulated.",
        "risk": "Low",
        "command": "None",
        "reversible": True,
        "rollback_description": "Diagnostic query; no rollback required."
    },
    "check_cpu_usage": {
        "action_name": "check_cpu_usage",
        "description": "Simulates querying processor utilization metrics.",
        "mode": "Simulation",
        "expected_result": "CPU usage diagnostic would be simulated.",
        "risk": "Low",
        "command": "None",
        "reversible": True,
        "rollback_description": "Diagnostic query; no rollback required."
    },
    "check_memory_usage": {
        "action_name": "check_memory_usage",
        "description": "Simulates querying system RAM and buffer memory allocation.",
        "mode": "Simulation",
        "expected_result": "Memory diagnostic would be simulated.",
        "risk": "Low",
        "command": "None",
        "reversible": True,
        "rollback_description": "Diagnostic query; no rollback required."
    },
    "simulate_failure": {
        "action_name": "simulate_failure",
        "description": "Diagnostic test hook configured to simulate an execution failure.",
        "mode": "Simulation",
        "expected_result": "Simulated failure response.",
        "risk": "Low",
        "command": "None",
        "reversible": True,
        "rollback_description": "Simulation failure hook; no rollback required."
    },
    "simulate_verification_failure": {
        "action_name": "simulate_verification_failure",
        "description": "Diagnostic test hook configured to simulate action success followed by verification failure.",
        "mode": "Simulation",
        "expected_result": "Action success with simulated verification check failure.",
        "risk": "Low",
        "command": "None",
        "reversible": True,
        "rollback_description": "Simulation failure hook; no rollback required."
    }
}


def get_action_metadata(action_name):
    """
    Returns safety and reversibility metadata for a given action name.
    """
    if action_name in ACTION_METADATA:
        return ACTION_METADATA[action_name]
    return {
        "action_name": action_name,
        "description": "Unknown unlisted action.",
        "mode": "Simulation",
        "expected_result": "Action is not in safe allowlist and would be rejected.",
        "risk": "High",
        "command": "None",
        "reversible": False,
        "rollback_description": "Action not recognized; no rollback plan available."
    }


def get_dry_run_preview(action_name):
    """
    Part 7: Generates a dry-run preview report without executing anything.
    Does NOT change incident status, execution status, or database state.
    """
    meta = get_action_metadata(action_name)
    is_safe = action_name in SAFE_ACTIONS
    return {
        "action_name": action_name,
        "mode": "Simulation",
        "expected_result": meta["expected_result"],
        "risk": meta["risk"],
        "actual_command": "None",
        "is_safe": is_safe,
        "reversible": "Yes" if meta["reversible"] else "No",
        "rollback_plan": meta["rollback_description"],
        "state_changes": "None (Dry-run mode does not modify state)"
    }


