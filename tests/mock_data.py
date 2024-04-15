def create_mock(**kwargs):
    return type("MockObject", (), kwargs)()

if __name__ == "__main__":
    m = create_mock(a=123,b="asdf")
    print(m.a)
    print(m.b)
    print(bytes(m.a, 'utf-8').decode('utf-8'))
    print(bytes(m.b, 'utf-8').decode('utf-8'))
