"""
This module contains all the enumerated structures used within GitMate.
"""
from enum import Enum


class PluginCategory(Enum):
    """
    Enum class to hold types of plugins.
    """
    # Plugin related to analysis
    ANALYSIS = 'analysis'
    # Plugin related to issues
    ISSUE = 'issue'
    # Plugin related to Pull Requests
    PULLS = 'pull_request'


class ScheduledTasks(Enum):
    """
    Task schedules type
    """
    # Scheduled to run daily
    DAILY = 1
    # Scheduled to run weekly
    WEEKLY = 2
    # Scheduled to run monthy
    MONTHLY = 3
