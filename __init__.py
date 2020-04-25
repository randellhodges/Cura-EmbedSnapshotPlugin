from . import EmbedSnapshotPlugin

def getMetaData():
    return {}

def register(app):
    return {"extension": EmbedSnapshotPlugin.EmbedSnapshotPlugin()}
