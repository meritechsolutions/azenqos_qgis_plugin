import random
from time import sleep
from qgis.core import *
from qgis.utils import *
from qgis.gui import *
from qgis.PyQt.QtCore import QVariant

MESSAGE_CATEGORY = 'RandomIntegerSumTask'

class CellLayerTask(QgsTask):
    def __init__(self, description, duration):
        super().__init__(description)
        self.duration = duration
        self.total = 0
        self.iterations = 0
        self.exception = None
    
    def run(self):
        # QgsMessageLog.logMessage('Started task "{}"'.format(
        #                              self.description()),
        #                          MESSAGE_CATEGORY, Qgis.Info)
        # wait_time = self.duration / 100
        # for i in range(100):
        #     sleep(wait_time)
        #     # use setProgress to report progress
        #     self.setProgress(i)
        #     arandominteger = random.randint(0, 500)
        #     self.total += arandominteger
        #     self.iterations += 1
        #     # check isCanceled() to handle cancellation
        #     if self.isCanceled():
        #         return False
        #     # simulate exceptions to show how to abort task
        #     if arandominteger == 42:
        #         # DO NOT raise Exception('bad value!')
        #         # this would crash QGIS
        #         self.exception = Exception('bad value!')
        #         return False
        return True

    def finished(self, result):
        """
        This function is automatically called when the task has
        completed (successfully or not).
        You implement finished() to do whatever follow-up stuff
        should happen after the task is complete.
        finished is always called from the main thread, so it's safe
        to do GUI operations and raise Python exceptions here.
        result is the return value from self.run.
        """

        
        # vl = QgsVectorLayer("Point", "temporary_points", "memory")
        # pr = vl.dataProvider()
        # # Enter editing mode
        # vl.startEditing()
        # # add fields
        # pr.addAttributes( [ QgsField("name", QVariant.String),
        #                 QgsField("age",  QVariant.Int),
        #                 QgsField("size", QVariant.Double) ] )
        # # add a feature
        # # To just create the layer and add features later, delete the four lines from here until Commit changes
        # fet = QgsFeature()
        # fet.setGeometry( QgsGeometry.fromPointXY(QgsPointXY(15,60)) )
        # fet.setAttributes(["Johny",20,0.3])
        # pr.addFeatures( [ fet ] )
        # # Commit changes
        # vl.commitChanges()
        # # Show in project
        # QgsProject.instance().addMapLayer(vl)

        # root = QgsProject.instance().layerTreeRoot()
        # layers = root.findLayers()
        # for la in layers:
        #     print(la)

        sourceCrs = QgsCoordinateReferenceSystem(4326)
        destCrs = QgsCoordinateReferenceSystem(4326)
        tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
        layer =  QgsVectorLayer('Polygon', 'poly' , "memory")
        pr = layer.dataProvider() 
        poly = QgsFeature()
        points = [(QgsPointXY(100.405295, 13.913899)),(QgsPointXY(100.405133, 13.914045)),(QgsPointXY(100.405433, 13.914048))]
        poly.setGeometry(QgsGeometry.fromPolygonXY([points]))
        pr.addFeatures([poly])
        layer.updateExtents()
        QgsProject.instance().addMapLayers([layer])
        
        # if result:
        #     QgsMessageLog.logMessage(
        #         'RandomTask "{name}" completed\n' \
        #         'RandomTotal: {total} (with {iterations} '\
        #       'iterations)'.format(
        #           name=self.description(),
        #           total=self.total,
        #           iterations=self.iterations),
        #       MESSAGE_CATEGORY, Qgis.Success)
        # else:
        #     if self.exception is None:
        #         QgsMessageLog.logMessage(
        #             'RandomTask "{name}" not successful but without '\
        #             'exception (probably the task was manually '\
        #             'canceled by the user)'.format(
        #                 name=self.description()),
        #             MESSAGE_CATEGORY, Qgis.Warning)
        #     else:
        #         QgsMessageLog.logMessage(
        #             'RandomTask "{name}" Exception: {exception}'.format(
        #                 name=self.description(),
        #                 exception=self.exception),
        #             MESSAGE_CATEGORY, Qgis.Critical)
        #         raise self.exception

    def cancel(self):
        # QgsMessageLog.logMessage(
        #     'RandomTask "{name}" was canceled'.format(
        #         name=self.description()),
        #     MESSAGE_CATEGORY, Qgis.Info)
        super().cancel()