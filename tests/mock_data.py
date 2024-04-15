def create_mock(**kwargs):
    return type("MockObject", (), kwargs)()

