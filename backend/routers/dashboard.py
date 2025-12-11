from fastapi import APIRouter
from plots.sample_dashboard import revenue_timeseries

router = APIRouter()


@router.get("/sample-revenue")
async def sample_revenue():
    fig = revenue_timeseries()
    return fig.to_dict()
