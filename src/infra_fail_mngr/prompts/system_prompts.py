def get_system_prompt():
    return f"""
        You are an Infrastructure crisis manager.
                
        Decide the next step. 
        - If you need information (e.g. Weather), call that tool.
        - If you are ready to fix, call 'assign_repair_crew'.
        """
