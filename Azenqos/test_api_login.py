import login_dialog


def test():
    raised = False
    try:
        login_dialog.login(
            {
                "server_url": "https://test0.azenqos.com/import_status",
                "login": "wronguser",
                "pass": "wrongpass",
            }
        )        
    except Exception as exstr:
        raised = True
        assert "Unauthorized" in str(exstr)

    assert raised == True

if __name__ == "__main__":
    test()
