from src.resources import faust_app

__all__ = ["stats_page"]


@faust_app.page("/stats/")
async def stats_page(self, request):
    return self.json(faust_app.monitor.asdict())
