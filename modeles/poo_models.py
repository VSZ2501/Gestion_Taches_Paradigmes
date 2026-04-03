class User:
    def __init__(self, user_id, name, email):
        self.id = user_id
        self.name = name
        self.email = email

class Project:
    def __init__(self, project_id, name, start_date, end_date):
        self.id = project_id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date

class Task:
    def __init__(self, task_id, title, status, due_date, priority, user_id=None, project_id=None):
        self.id = task_id
        self.title = title
        self.status = status
        self.due_date = due_date
        self.priority = priority
        self.user_id = user_id
        self.project_id = project_id

class SimpleTask(Task):
    def __init__(self, task_id, title, status, due_date, priority, user_id=None, project_id=None):
        super().__init__(task_id, title, status, due_date, priority, user_id, project_id)
        self.task_type = "Simple"

class ComplexTask(Task):
    def __init__(self, task_id, title, status, due_date, priority, dependencies=None, user_id=None, project_id=None):
        super().__init__(task_id, title, status, due_date, priority, user_id, project_id)
        self.task_type = "Complex"
        # Une tâche complexe peut avoir des dépendances vers d'autres tâches
        self.dependencies = dependencies if dependencies is not None else []