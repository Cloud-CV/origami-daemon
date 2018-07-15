class OrigamiException(Exception):
    """
    Base class for all exceptions thrown by origami.
    """
    STATUS_CODE = 1

    def __init__(self, message=''):
        super().__init__("CV_OrigamiException[{0}] => {1}".format(
            self.STATUS_CODE, message))


class OrigamiConfigException(OrigamiException):
    """
    Bundled zip provided by user or by server is not valid.
    """
    STATUS_CODE = 100


class InvalidDemoBundleException(OrigamiException):
    """
    Bundled zip provided by user or by server is not valid.
    """
    STATUS_CODE = 200


class OrigamiDockerConnectionError(OrigamiException):
    """
    Error when origami throws an exception when trying to connect
    or use docker.
    """
    STATUS_CODE = 300
