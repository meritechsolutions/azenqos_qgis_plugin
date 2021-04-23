import azq_server_api


def test():
    raised = False
    try:
        azq_server_api.api_login_get_token(
            "https://test0.azenqos.com/some_path",
            "wronguser",
            "wrongpass",
        )
    except Exception as exstr:
        raised = True
        assert "Unauthorized" in str(exstr)

    assert raised == True


if __name__ == "__main__":
    test()
