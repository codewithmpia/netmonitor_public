# -*- coding: utf-8 -*-
"""
    filters.py
    ~~~~~~~~~~~~~
    Custom filters for Jinja2 templates.
"""


def format_bytes(size):
    """Format bytes to human readable format"""
    if not size:
        return "0 B"
    
    try:
        size = float(size)  # Assurer que size est un nombre
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        i = 0
        while size >= 1024 and i < len(units) - 1:
            size /= 1024
            i += 1
        
        return f"{round(size, 2)} {units[i]}"
    except (TypeError, ValueError):
        return "0 B"