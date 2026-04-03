def check_access(user_role, doc_role):
    if user_role == "c_level":
        return True
    return user_role == doc_role