from ..services.system_service import SystemInfoService

class SystemViewModel:
    def __init__(self):
        self.service = SystemInfoService()

    def get_stats(self):
        return self.service.get_system_info()