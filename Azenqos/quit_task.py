import time

try:
    from qgis.core import (
        QgsProject,
        QgsTask,
        QgsMessageLog,
        QgsRasterLayer,
        QgsRectangle,
        QgsLayerTreeLayer,
        QgsMapLayerType,
        QgsCoordinateReferenceSystem,
    )
except:
    pass


class QuitTask(QgsTask):
    def __init__(self, desc, azenqosMain):
        QgsTask.__init__(self, desc)
        self.start_time = time.time()
        self.desc = desc
        self.exception = None
        self.azqMain = azenqosMain

    def run(self):
        QgsMessageLog.logMessage(
            "[-- Start Removing Dependencies --]", tag="Processing"
        )
        self.start_time = time.time()
        return True

    def finished(self, result):
        if result:
            elapsed_time = time.time() - self.start_time
            QgsMessageLog.logMessage(
                "Elapsed time: " + str(elapsed_time) + " s.", tag="Processing"
            )
            QgsMessageLog.logMessage(
                "[-- End Removing Dependencies --]", tag="Processing"
            )
            """
            if self.azqMain.newImport is False:
                self.azqMain.databaseUi.removeMainMenu()
            """
        else:
            if self.exception is None:
                QgsMessageLog.logMessage(
                    'Task "{name}" not successful but without '
                    "exception (probably the task was manually "
                    "canceled by the user)".format(name=self.desc),
                    tag="Exception",
                )
            else:
                QgsMessageLog.logMessage(
                    'Task "{name}" Exception: {exception}'.format(
                        name=self.desc, exception=self.exception
                    ),
                    tag="Exception",
                )
                raise self.exception
