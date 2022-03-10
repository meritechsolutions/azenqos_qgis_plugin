import integration_test_helpers
import azq_server_api
from PyQt5.QtWidgets import QApplication
import predict_widget

def test():
    return
    app = QApplication([])
    print("app: ", app)  # use it so pyflakes wont complain - we need a ref to qapplicaiton otherwise we'll get segfault
    gvars = integration_test_helpers.get_global_vars()
    w = predict_widget.predict_widget(None, gvars)
    models_df = azq_server_api.api_predict_models_list_df(gvars.login_dialog.server, gvars.login_dialog.token)
    models_df = predict_widget.sort_models_df(models_df)
    models_text = models_df.apply(w.model_row_to_text_sum, axis=1)
    print("models_text:", models_text.values.tolist())

if __name__ == "__main__":
    test()